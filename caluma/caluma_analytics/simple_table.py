from __future__ import annotations  # self-referencing annotations

import re
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from functools import cached_property, partial
from typing import List, Optional

from django.conf import settings
from django.db import connection
from django.utils import timezone
from psycopg2.extras import DictCursor

from caluma.caluma_form import models as form_models
from caluma.caluma_workflow import models as workflow_models

from . import models, sql


class BaseField:
    """Base class for all (available) fields."""

    def __init__(
        self,
        *,
        parent: Optional[BaseField],
        identifier: str,
        visibility_source,
        label=None,
        **_,
    ):
        """Initialize new field instance.

        Parameters are as follows:
         - `parent`: an optional reference to the superordinate field
         - `identifier`: the DB field that's being extracted
         - `visibility_source`: Helper to fetch visibility-aware querysets
         - `label`: Optional label
        """
        self.parent = parent
        self.identifier = identifier
        self.visibility_source = visibility_source
        self.label = label if label else identifier
        self.filters = None

        # required - set to True if the result of this field is
        # needed in the analysis.
        # Optimisation - SQL generation may be skipped in some
        # cases if field not required
        self.required = False
        self.show_output = True

    def path_args(self):
        """Extract arguments from the field's path."""
        match = re.match(r"^\w+?\[(.*)\]$", self.identifier)
        if match:
            return match.group(1).split(",")
        return []  # pragma: no cover

    @property
    def available_children(self):  # pragma: no cover
        """Return a dict of all available children.

        Used in the construction/design-time stage,
        as well as when building an SQL query from a given
        set of paths.
        """
        return {}

    def full_label(self):
        """Return a full hierarchical path to the given field.

        Includes the full label of the parent field(s) as well
        """
        if self.parent:
            return f"{self.parent.full_label()} > {self.label}"
        return self.label

    def source_path(self) -> List[str]:
        """Return the full source path of this field as a list."""
        return (
            self.parent.source_path() + [self.identifier]
            if self.parent
            else [self.identifier]
        )

    def parse_value(self, value):
        """Parse value from DB into python value.

        Ensure date / time types are using the correct timezone,
        and numeric types are int or float.
        """
        if isinstance(value, Decimal):
            # Postgres sometimes returns Decimal types that
            # need to be converted for "proper" representation
            # in the output. Depends on PostgreSQL version
            # whether this is triggered or not
            return float(value)  # pragma: no cover

        if isinstance(value, datetime):
            # psycopg2 returns "generic" tz info dates that sometimes
            # are weird when comparing to the ones Django expects
            # (Note they're still correct, just not labeled in a
            # useful way)
            current_tz = timezone.get_current_timezone()
            return current_tz.normalize(value)

        return value

    def query_field(self):
        """Return the corresponding SQL rendering field."""
        raise NotImplementedError(
            f"Method 'query_field' is missing in {type(self)}"
        )  # pragma: no cover

    def is_value(self):
        """Return True if this field represents a usable value."""
        raise NotImplementedError(
            f"Method 'is_value' is missing in {type(self)}"
        )  # pragma: no cover

    def is_leaf(self):
        """Return True if there are no more fields below this one."""
        raise NotImplementedError(
            f"Method 'is_leaf' is missing in {type(self)}"
        )  # pragma: no cover

    def supported_functions(self):
        """Return list of supported aggregate functions.

        In all cases, at least VALUE should be returned. Depending on
        data type of the field, additional functions can be supported.
        """
        raise NotImplementedError(
            f"Method 'supported_functions' is missing in {type(self)}"
        )  # pragma: no cover

    def _all_supported_functions(self):
        """Return a list of all functions that Analytics supports.

        call this in supported_functions() implementations if there
        is no restriction on supported functions in the field.
        """
        return [func.upper() for func, _ in models.AnalyticsField.FUNCTION_CHOICES]


class MetaField(BaseField):
    """MetaField implements access to JSON fields and their contents.

    For this to work correctly, the setting META_FIELDS must be
    configured to list the fields that can be extracted.
    If a key is set in a `meta` value but not listed in the
    settings, it will not be usable in Analytics.
    """

    def __init__(self, parent, identifier, label, *, visibility_source, meta_name=None):
        super().__init__(
            parent=parent,
            identifier=identifier,
            label=label,
            visibility_source=visibility_source,
        )
        self.meta_name = meta_name

    def is_leaf(self):
        # if we have a meta field name, we are a leaf:
        # We cannot descend further down, there are no children
        return bool(self.meta_name)

    def supported_functions(self):
        # meta is kind of special - we don't know what type of data people
        # put into those fields, so we support all functions despite some
        # of them might not work
        return self._all_supported_functions()

    def is_value(self):
        # "plain" meta cannot be used as a value
        return self.is_leaf()

    @cached_property
    def available_children(self):
        if self.meta_name:
            return {}
        return {
            name: MetaField(
                parent=self,
                identifier=self.identifier,
                label=f"Key '{name}'",
                meta_name=name,
                visibility_source=self.visibility_source,
            )
            for name in settings.META_FIELDS
        }

    def source_path(self):
        source_path = super().source_path()
        if self.meta_name:
            # replace last element with our "meta" name
            # so path is correct, and identifier still can point
            # to the actual DB field.
            source_path[-1] = self.meta_name
        return source_path

    def query_field(self):
        if self.meta_name:
            return sql.JSONExtractorField(
                self.identifier,
                parent=self.parent.query_field() if self.parent else None,
                json_key=self.meta_name,
            )
        return sql.NOOPField(
            self.identifier,
            parent=self.parent.query_field() if self.parent else None,
        )


class AttributeField(BaseField):
    """Extractor for regular table attributes.

    When `is_date` is set, it will also contain a number of sub-fields
    that represent extracts of some date parts (such as year, quarter,
    month, and weekday).
    """

    def __init__(self, parent, identifier, *, visibility_source, is_date=False):
        super().__init__(
            parent=parent, identifier=identifier, visibility_source=visibility_source
        )
        self.is_date = is_date

    def is_leaf(self):
        return not self.is_date

    def is_value(self):
        return True

    def supported_functions(self):
        return [
            models.AnalyticsField.FUNCTION_VALUE.upper(),
            models.AnalyticsField.FUNCTION_MAX.upper(),
            models.AnalyticsField.FUNCTION_MIN.upper(),
        ]

    def query_field(self):
        if self.is_date and not self.required:
            return sql.NOOPField(
                self.identifier,
                parent=self.parent.query_field() if self.parent else None,
            )
        return sql.AttrField(
            self.identifier,
            parent=self.parent.query_field() if self.parent else None,
        )

    @cached_property
    def available_children(self):
        if self.is_date:
            # for FormAnswerField, the identifier is the question slug,
            # but the field is 'date'
            date_field = getattr(self, "attr_name", self.identifier)

            extractor_field = partial(
                DateExtractorField,
                parent=self,
                date_field=date_field,
                visibility_source=self.visibility_source,
            )
            return {
                "year": extractor_field(identifier="year"),
                "month": extractor_field(identifier="month"),
                "weekday": extractor_field(identifier="weekday"),
                "quarter": extractor_field(identifier="quarter"),
            }
        return {}


class WorkItemField(BaseField):
    """Field that provides access to a work item's data."""

    ORDER_TYPES = {
        "first": ["created_at"],
        "last": ["created_at DESC"],
        "firstclosed": ["closed_at"],
        "lastclosed": ["closed_at DESC"],
    }
    ORDER_LABELS = {
        "first": "first created",
        "last": "last created",
        "firstclosed": "first closed",
        "lastclosed": "first closed",
    }

    def __init__(
        self,
        parent,
        identifier,
        visibility_source,
        task_slug=None,
        ordering_selector=None,
    ):
        super().__init__(
            parent=parent, identifier=identifier, visibility_source=visibility_source
        )

        self.task_slug = task_slug if task_slug else self.path_args()[0]
        self.ordering_selector = (
            ordering_selector if ordering_selector else self.path_args()[1]
        )
        assert self.ordering_selector in self.ORDER_TYPES

        # TODO translate?
        self.label = f"Workitem: {self.ORDER_LABELS[self.ordering_selector]} with task {self.task_slug}"

    def _order_by(self):
        return self.ORDER_TYPES[self.ordering_selector]

    def is_leaf(self):
        return False

    def is_value(self):
        return False

    def supported_functions(self):
        return []

    def query_field(self):
        return sql.JoinField(
            self.identifier,
            table=self.visibility_source.work_items(),
            outer_ref=("id", "case_id"),
            filters=[f"task_id = '{self.task_slug}'"],
            order_by=self._order_by(),
            parent=self.parent.query_field() if self.parent else None,
        )

    @cached_property
    def available_children(self):
        direct_fields = {
            "meta": MetaField(
                parent=self,
                identifier="meta",
                label="Meta",
                visibility_source=self.visibility_source,
            ),
            "closed_at": AttributeField(
                parent=self,
                identifier="closed_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "deadline": AttributeField(
                parent=self,
                identifier="closed_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "created_at": AttributeField(
                parent=self,
                identifier="created_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "status": AttributeField(
                parent=self,
                identifier="status",
                visibility_source=self.visibility_source,
            ),
            "name": AttributeField(
                parent=self, identifier="name", visibility_source=self.visibility_source
            ),
        }

        wi_forms = form_models.Form.objects.filter(
            documents__work_item__isnull=False
        ).distinct()

        form_fields = {
            f"document[{form.slug}]": FormDocumentField(
                identifier=f"document[{form.slug}]",
                parent=self,
                visibility_source=self.visibility_source,
            )
            for form in wi_forms
        }

        return {**direct_fields, **form_fields}


class FormDocumentField(BaseField):
    """Field that provides access to a form's data."""

    def __init__(
        self, parent, identifier, visibility_source, subform_level=0, form_slug=None
    ):
        super().__init__(
            parent=parent, identifier=identifier, visibility_source=visibility_source
        )

        self.form_slug = form_slug if form_slug else self.path_args()[0]

        # subform level is used so we can have the "path" as it is presented
        # to the user (our `location`) separate from where the corresponding
        # `Answer` is found (remember, answers of questions in subforms are
        # NOT put into sub-documents according to hierarchy, but stored in a
        # single document!)
        self.subform_level = subform_level

    def query_field(self):
        # Only for top-level form do we need a Join field.
        # The "sub-forms"' answers are all on the same document,
        # thus for those we return a NOOP field.
        if self.subform_level == 0:
            return sql.JoinField(
                self.identifier,
                table=self.visibility_source.documents(),
                outer_ref=("document_id", "id"),
                filters=[f"form_id = '{self.form_slug}'"],
                parent=self.parent.query_field() if self.parent else None,
            )
        # else - we just return the field from our "virtual" parent
        return self.parent.query_field()

    def is_leaf(self):
        return False

    def is_value(self):
        return False

    def supported_functions(self):
        return []

    @cached_property
    def available_children(self):
        form = form_models.Form.objects.get(pk=self.form_slug)
        questions = form.questions.all().exclude(type=form_models.Question.TYPE_TABLE)
        children = {}

        for question in questions:
            qf = self._question_field(question)
            if qf:
                children[question.pk] = qf
        return children

    def _question_field(self, question):
        # Note: we explicitly don't support table questions at the moment.
        # They would require another sub-selector to get the first, or last
        # item in the table, which in most cases in real-world use isn't very
        # useful.
        if question.type in (
            question.TYPE_INTEGER,
            question.TYPE_FLOAT,
            question.TYPE_TEXT,
            question.TYPE_TEXTAREA,
            question.TYPE_CHOICE,
            question.TYPE_DYNAMIC_CHOICE,
        ):
            return FormAnswerField(
                parent=self,
                identifier=question.slug,
                attr_name="value",
                subform_level=self.subform_level,
                visibility_source=self.visibility_source,
            )
        elif question.type == question.TYPE_DATE:
            return FormAnswerField(
                parent=self,
                identifier=question.slug,
                attr_name="date",
                is_date=True,
                subform_level=self.subform_level,
                visibility_source=self.visibility_source,
            )

        elif question.type == question.TYPE_FORM:
            return FormDocumentField(
                parent=self,
                identifier=question.slug,
                form_slug=question.sub_form_id,
                subform_level=self.subform_level + 1,
                visibility_source=self.visibility_source,
            )


class DirectDocumentField(FormDocumentField):
    """Field that directly represents a document on top level.

    This is used only for the "Documents" starting object, as here,
    the main table is already the "document".
    """

    def query_field(self):
        return sql.NOOPField(
            self.identifier,
            parent=self.parent.query_field() if self.parent else None,
        )


class FormAnswerField(AttributeField):
    """Represents access to an answer within a form."""

    def __init__(self, parent, identifier, attr_name, subform_level, **kwargs):
        super().__init__(parent=parent, identifier=identifier, **kwargs)
        self.subform_level = subform_level
        self.attr_name = attr_name

    def supported_functions(self):
        question = form_models.Question.objects.get(pk=self.identifier)
        base_functions = [
            models.AnalyticsField.FUNCTION_VALUE.upper(),
            models.AnalyticsField.FUNCTION_COUNT.upper(),
        ]
        text_functions = [
            models.AnalyticsField.FUNCTION_MAX.upper(),
            models.AnalyticsField.FUNCTION_MIN.upper(),
        ]
        numeric_functions = [
            models.AnalyticsField.FUNCTION_MAX.upper(),
            models.AnalyticsField.FUNCTION_MIN.upper(),
            models.AnalyticsField.FUNCTION_AVERAGE.upper(),
            models.AnalyticsField.FUNCTION_SUM.upper(),
        ]
        function_support = {
            form_models.Question.TYPE_CHOICE: text_functions,
            form_models.Question.TYPE_TEXT: text_functions,
            form_models.Question.TYPE_TEXTAREA: text_functions,
            form_models.Question.TYPE_DATE: text_functions,
            form_models.Question.TYPE_INTEGER: numeric_functions,
            form_models.Question.TYPE_FLOAT: numeric_functions,
        }

        return base_functions + function_support[question.type]

    def query_field(self):
        # Only for top-level form do we need a Join field.
        # The "sub-forms"' answers are all on the same document,
        # thus for those we return a NOOP field.
        answer_join_field = sql.JoinField(
            identifier=self.identifier,
            table=self.visibility_source.answers(),
            # TODO: turn this into SQL parameter
            filters=[f""""question_id" = '{self.identifier}' """],
            outer_ref=("id", "document_id"),
            parent=self.parent.query_field() if self.parent else None,
        )
        value_field = sql.AttrField(
            identifier=self.attr_name,
            parent=answer_join_field,
            filter_values=self.filters,
            answer_value_mode=(self.attr_name == "value"),
        )
        return value_field


class DateExtractorField(AttributeField):
    """Specialisation of attribute field: Extract a date part."""

    def __init__(self, parent, identifier, visibility_source, date_field, **kwargs):
        super().__init__(
            parent,
            identifier,
            visibility_source=visibility_source,
            is_date=False,
            **kwargs,
        )
        self.date_field = date_field

    def supported_functions(self):
        return self._all_supported_functions()

    def query_field(self):
        return sql.DateExprField(
            self.date_field,
            parent=self.parent.query_field() if self.parent else None,
            extract_part=self.identifier,
            filter_values=self.filters,
        )

    def parse_value(self, value):
        """Convert extracted date part to integer.

        This is necessary because not all supported postgres versions return the
        same datatype which leads to inconsistency. E.g versions < 12 returns a
        float while later versions return a decimal.
        """
        return int(value)


class BaseStartingObject:
    """Base class for starting objects.

    Provides interface for listing the fields within the given starting
    object, and also supports Enum generation on the GraphQL side.
    """

    def __init__(self, info, disable_visibilities):
        """Initialize starting object.

        The `info` parameter is the Graphql info/context object.
        """
        self.info = info

        # deferred import to avoid circular deps
        from . import visibility

        self.visibility_source = visibility.CalumaVisibilitySource(
            info, is_disabled=disable_visibilities
        )

    @classmethod
    def get_object(cls, identifier, info, disable_visibilities=False):
        """Return starting object identified by given name.

        Call `BaseStartingObject.get_object('cases', info)`
        to get a CaseStartingObject, for example.
        """

        subclasses_by_name = {sub.identifier: sub for sub in cls.__subclasses__()}
        return subclasses_by_name[identifier](
            info, disable_visibilities=disable_visibilities
        )

    @classmethod
    def as_choices(cls):
        """Return a list of (slug, label) tuples of all available starting objects.

        This can then be used in a CharField's choices.
        """

        objects = sorted(
            cls.__subclasses__(),
            key=lambda obj: obj.label,
        )
        return [(obj.identifier, obj.label) for obj in objects]

    def get_fields(self, prefix=None, depth=1):
        """Return fields for the GraphQL interface.

        When not parametrized, return the root fields of the starting object.

        When a given prefix and depth are given, return the fields from the
        specified sub-path, and go down the requested depth.
        """
        if prefix:
            # support string prefixes as well
            prefix = prefix if isinstance(prefix, list) else prefix.split(".")

        def _children_at_depth(field, _depth):
            if _depth <= 0:
                return
            for path, child in field.available_children.items():
                yield ([path], child)
                for subpath, grandchild in _children_at_depth(child, _depth - 1):
                    yield ([path] + subpath, grandchild)

        if prefix:
            # get only fields with given prefix, and start looking
            # down `depth` levels from there
            fields = self.get_field(prefix).available_children
        else:
            prefix = []
            fields = self.root_fields()

        output = {}
        for path, field in fields.items():

            output[".".join(prefix + [path])] = field
            for subpath, child in _children_at_depth(field, depth - 1):
                output[".".join(prefix + [path] + subpath)] = child
        return output

    def root_fields(self):  # pragma: no cover
        """Return the root fields for this starting object.

        Must be overridden in a subclass actually implementing
        a starting object.
        """
        raise NotImplementedError("Must be implemented in BaseStartingObject subclass")

    def get_field(self, path):
        """Return a single field with the given path."""
        children = self.root_fields()
        for elem in path:
            field = children[elem]
            children = field.available_children
        return field


class CaseStartingObject(BaseStartingObject):
    identifier = "cases"
    label = "Cases"

    def get_query(self):
        return self.visibility_source.cases()

    def root_fields(self):
        direct_fields = {
            "meta": MetaField(
                parent=None,
                identifier="meta",
                label="Meta",
                visibility_source=self.visibility_source,
            ),
            "closed_at": AttributeField(
                parent=None,
                identifier="closed_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "created_at": AttributeField(
                parent=None,
                identifier="created_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "status": AttributeField(
                parent=None,
                identifier="status",
                visibility_source=self.visibility_source,
            ),
            "id": AttributeField(
                parent=None,
                identifier="id",
                visibility_source=self.visibility_source,
            ),
        }

        case_forms = form_models.Form.objects.filter(
            documents__case__isnull=False
        ).distinct()

        form_fields = {
            f"document[{form.slug}]": FormDocumentField(
                identifier=f"document[{form.slug}]",
                parent=None,
                visibility_source=self.visibility_source,
            )
            for form in case_forms
        }

        tasks = workflow_models.Task.objects.all()

        workitem_fields = {
            f"workitem[{task.slug},{selector}]": WorkItemField(
                identifier=f"workitem[{task.slug},{selector}]",
                parent=None,
                visibility_source=self.visibility_source,
            )
            for selector in ["first", "last", "firstclosed", "lastclosed"]
            for task in tasks
        }

        return {**direct_fields, **form_fields, **workitem_fields}


class WorkItemsStartingObject(BaseStartingObject):
    identifier = "work_items"
    label = "Work Items"

    def get_query(self):
        return self.visibility_source.work_items()

    def root_fields(self):
        direct_fields = {
            "meta": MetaField(
                parent=None,
                identifier="meta",
                label="Meta",
                visibility_source=self.visibility_source,
            ),
            "task_id": AttributeField(
                parent=None,
                identifier="task_id",
                is_date=False,
                visibility_source=self.visibility_source,
            ),
            "closed_at": AttributeField(
                parent=None,
                identifier="closed_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "created_at": AttributeField(
                parent=None,
                identifier="created_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
            "status": AttributeField(
                parent=None,
                identifier="status",
                visibility_source=self.visibility_source,
            ),
            "id": AttributeField(
                parent=None,
                identifier="id",
                visibility_source=self.visibility_source,
            ),
        }

        workitem_forms = form_models.Form.objects.filter(
            documents__work_item__isnull=False
        ).distinct()

        form_fields = {
            f"document[{form.slug}]": FormDocumentField(
                identifier=f"document[{form.slug}]",
                parent=None,
                visibility_source=self.visibility_source,
            )
            for form in workitem_forms
        }

        return {**direct_fields, **form_fields}


class DocumentsStartingObject(BaseStartingObject):
    identifier = "documents"
    label = "documents"

    def get_query(self):
        return self.visibility_source.documents()

    def root_fields(self):
        direct_fields = {
            "id": AttributeField(
                parent=None,
                identifier="id",
                visibility_source=self.visibility_source,
            ),
            "meta": MetaField(
                parent=None,
                identifier="meta",
                label="Meta",
                visibility_source=self.visibility_source,
            ),
            "form_id": AttributeField(
                parent=None,
                identifier="form_id",
                is_date=False,
                visibility_source=self.visibility_source,
            ),
            "created_at": AttributeField(
                parent=None,
                identifier="created_at",
                is_date=True,
                visibility_source=self.visibility_source,
            ),
        }

        form_fields = {
            f"answers[{form.slug}]": DirectDocumentField(
                identifier=f"answers[{form.slug}]",
                parent=None,
                visibility_source=self.visibility_source,
            )
            for form in form_models.Form.objects.all()
        }

        return {**direct_fields, **form_fields}


class SimpleTable:
    class _AnonymousInfo:
        """
        Pseudo GraphQL info object.

        Used for commandline access, so the commandline version
        can also invoke the visibilities.
        """

        context = {}

    def __init__(self, table, info=_AnonymousInfo, is_summary=False):
        self.info = info
        self.table = table
        self.last_query = None
        self.last_query_params = None
        self.is_summary = is_summary

        self.starting_object = BaseStartingObject.get_object(
            self.table.starting_object,
            self.info,
            disable_visibilities=self.table.disable_visibilities,
        )

        self.base_query = sql.Query(from_=self.starting_object.get_query())

    @cached_property
    def _fields(self):
        field_spec_qs = self.table.fields.all()
        if self.is_summary:
            field_spec_qs = field_spec_qs.exclude(
                function=models.AnalyticsField.FUNCTION_VALUE
            )
        # sort fields to join by length. This way, parent fields
        # will be already joined when their children get added, so
        # they will have the right alias.
        table_fields = sorted(field_spec_qs, key=lambda f: len(f.data_source))

        fields = {}
        for field_spec in table_fields:
            fields[field_spec.alias] = self.starting_object.get_field(
                field_spec.data_source.split(".")
            )
            fields[field_spec.alias].alias = field_spec.alias
            fields[field_spec.alias].show_output = field_spec.show_output

            # Filters must always be on the outermost (base) query,
            # as we're using LEFT JOINs to get at related data.
            self.base_query.add_field_filter(
                self._sql_alias(field_spec.alias), field_spec.filters
            )
        return fields

    def get_sql_and_params(self):
        """Return a list of records as specified in the given table config."""

        base_query = self.get_query_object()

        sql_query, params, _ = sql.QueryRender(base_query).as_sql(alias=None)

        self.last_query = sql_query
        self.last_query_params = params
        return sql_query, params

    def get_query_object(self):

        fields = self._fields

        step_queries = {}
        base_query = deepcopy(self.base_query)

        for alias, field in fields.items():
            query = base_query

            field.required = True
            sql_field = field.query_field()
            sql_field.alias = self._sql_alias(alias)

            cache_path = ""
            for step in sql_field.path_from_root():
                cache_path = f"{cache_path}.{step.identifier}"
                if cache_path in step_queries:
                    query = step_queries[cache_path]
                else:
                    query = step.annotate(query)
                    step_queries[cache_path] = query

        return base_query

    def get_records(self):

        sql_query, params = self.get_sql_and_params()

        with connection.connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_query, params)
            data = cursor.fetchall()

            return [
                {
                    field.alias: field.parse_value(
                        row[f"analytics_result_{field.alias}"]
                    )
                    for field in self._fields.values()
                    if field.show_output
                }
                for row in data
            ]

    def get_summary(self):
        # simple tables can't do summary, but we must implement
        # it as both table types share the same GQL interface
        return {}  # pragma: no cover

    def _sql_alias(self, user_alias):
        return f"analytics_result_{user_alias}"
