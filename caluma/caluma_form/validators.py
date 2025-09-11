import sys
from datetime import date
from logging import getLogger

from django_filters.constants import EMPTY_VALUES
from rest_framework import exceptions

from caluma.caluma_core.exceptions import ConfigurationError
from caluma.caluma_data_source.data_source_handlers import get_data_sources
from caluma.caluma_form import structure
from caluma.caluma_workflow.models import Case

from . import jexl, models
from .format_validators import get_format_validators
from .models import DynamicOption, Question

log = getLogger()


class CustomValidationError(exceptions.ValidationError):
    """Custom validation error to carry more information.

    This can carry more information about the error, so the documentValidity
    query can show more useful information.
    """

    def __init__(self, detail, code=None, slugs=None):
        slugs = slugs if slugs else []
        super().__init__(detail, code)
        self.slugs = slugs


class AnswerValidator:
    def _validate_question_text(self, question, value, **kwargs):
        min_length = question.min_length if question.min_length is not None else 0
        max_length = (
            question.max_length if question.max_length is not None else sys.maxsize
        )

        if (
            not isinstance(value, str)
            or len(value) < min_length
            or len(value) > max_length
        ):
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type str, and it's length between {min_length} and {max_length}",
                slugs=[question.slug],
            )

    def _validate_question_textarea(self, question, value, **kwargs):
        self._validate_question_text(question, value)

    def _validate_question_float(self, question, value, **kwargs):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, float) or value < min_value or value > max_value:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type float, not lower than {min_value} "
                f"and not greater than {max_value}",
                slugs=[question.slug],
            )

    def _validate_question_integer(self, question, value, **kwargs):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, int) or value < min_value or value > max_value:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type int, not lower than {min_value} "
                f"and not greater than {max_value}",
                slugs=[question.slug],
            )

    def _validate_question_date(self, question, value, **kwargs):
        if not isinstance(value, date):
            raise CustomValidationError(
                f"Invalid value {value}. Should be of type date.", slugs=[question.slug]
            )

    def _structure_field(self, document, question, validation_context):
        """Return the requested structure field, and the root context.

        The root context is mostly not used, but needed to ensure it won't go
        out of scope before the field (form structure has only weakrefs from
        child to parent, and we don't want the parent to go out of scope, as it
        will break child (field) behaviour).
        """
        if validation_context:  # pragma: todo cover
            # Note about coverage: This is in fact covered, but in some python
            # versions, pytest-cov fails to see it when run with xdist, and I
            # don't have the patience to actually debug that stuff right now
            # The test that covers this branch is here:
            # `caluma_form.tests.test_option.test_validate_form_with_jexl_option`

            # If valdiation context is passed in from the DocumentValidator, we
            # already have the *field* we need, and no further work is needed.
            if validation_context.slug() != question.slug:  # pragma: no cover
                # This only happens if *programmer* made an error, therefore we're
                # not explicitly covering it
                raise ConfigurationError(
                    f"Passed validation context does not belong to question {question.slug}"
                )
            return validation_context, validation_context.get_root()

        # If we need to create the context ourselves here, we'll need to fetch
        # the field from the context.
        validation_context = DocumentValidator().get_validation_context(document)
        return validation_context.get_field(question.slug), validation_context

    def _evaluate_options_jexl(
        self, document, question, validation_context=None, qs=None
    ):
        """Return a list of slugs that are, according to their is_hidden JEXL, visible."""

        if not document and not validation_context:
            # Saving options of a default answer. Can't evaluate the options'
            # JEXL anyway, so allow all of them (and hit the DB, don't optimize
            # and use the structure code)
            return [o.slug for o in question.options.all()]

        elif not validation_context:
            # First see if we really need to build up the validation context. If
            # not, we can speed things up significantly
            all_options = list(question.options.all())
            if all(opt.is_hidden in ("false", "") for opt in all_options):
                # no JEXL evaluation neccessary
                return [o.slug for o in all_options]

        field, _root = self._structure_field(document, question, validation_context)
        if not field:  # pragma: no cover
            # This only happens if *programmer* made an error, therefore we're
            # not explicitly covering it
            raise ConfigurationError(
                f"Field for question '{question.slug}' not found "
                f"in form '{document.form_id}'"
            )

        options = field.get_options()
        return [o.slug for o in options if not field.evaluate_jexl(o.is_hidden)]

    def visible_options(self, document, question, qs):
        return self._evaluate_options_jexl(document, question, qs=qs)

    def _validate_question_choice(
        self, question, value, validation_context, document, **kwargs
    ):
        options = self._evaluate_options_jexl(
            document, question, validation_context=validation_context
        )

        if not isinstance(value, str) or value not in options:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and one of the options {', '.join(options)}",
                slugs=[question.slug],
            )

    def _validate_question_multiple_choice(
        self, question, value, validation_context, document, **kwargs
    ):
        options = self._evaluate_options_jexl(
            document, question, validation_context=validation_context
        )

        invalid_options = set(value) - set(options)
        if not isinstance(value, list) or invalid_options:
            raise CustomValidationError(
                f"Invalid options [{', '.join(invalid_options)}]. "
                f"Should be one of the options [{', '.join(options)}]",
                slugs=[question.slug],
            )

    def _validate_question_dynamic_choice(
        self, question, value, document, user, data_source_context, **kwargs
    ):
        if not isinstance(value, str):
            raise CustomValidationError(
                f'Invalid value "{value}". Must be of type str.', slugs=[question.slug]
            )

        self._validate_dynamic_option(
            question, document, value, user, data_source_context
        )
        self._remove_unused_dynamic_options(question, document, [value])

    def _validate_question_dynamic_multiple_choice(
        self, question, value, document, user, data_source_context, **kwargs
    ):
        if not isinstance(value, list):
            raise CustomValidationError(
                f'Invalid value: "{value}". Must be of type list', slugs=[question.slug]
            )

        for v in value:
            if not isinstance(v, str):
                raise CustomValidationError(
                    f'Invalid value: "{v}". Must be of type string',
                    slugs=[question.slug],
                )
            self._validate_dynamic_option(
                question, document, v, user, data_source_context
            )

        self._remove_unused_dynamic_options(question, document, value)

    def _validate_dynamic_option(
        self, question, document, option, user, data_source_context
    ):
        data_source = get_data_sources(dic=True)[question.data_source]
        data_source_object = data_source()

        valid_label = data_source_object.validate_answer_value(
            option, document, question, user, data_source_context
        )
        if valid_label is False:
            raise CustomValidationError(
                f'Invalid value "{option}". Not a valid option.', slugs=[question.slug]
            )

        DynamicOption.objects.get_or_create(
            document=document,
            question=question,
            slug=option,
            defaults={
                "label": valid_label,
                "created_by_user": user.username,
                "created_by_group": user.group,
            },
        )

    def _remove_unused_dynamic_options(self, question, document, used_values):
        DynamicOption.objects.filter(document=document, question=question).exclude(
            slug__in=used_values
        ).delete()

    def _validate_question_table(
        self,
        question,
        value,
        document,
        user,
        validation_context: structure.RowSet,
        instance=None,
        origin=False,
        **kwargs,
    ):
        if not origin:
            # Rowsets should always be validated in context, so we can use that
            for row in validation_context.children():
                DocumentValidator().validate(
                    row._document, user=user, **kwargs, validation_context=row
                )
            return

        # this answer was the entry-point of the validation
        # -> validate row form
        value = value or instance and instance.documents.all() or []
        question = question or instance and instance.question

        for row_doc in value:
            if row_doc.form_id != question.row_form_id:
                raise exceptions.ValidationError(
                    f"Document {row_doc.pk} is not of form type {question.row_form.pk}."
                )

    def _validate_question_files(self, question, value, **kwargs):
        if not isinstance(value, list) and value is not None:  # pragma: no cover
            # should already have been rejected by schema / gql level
            raise exceptions.ValidationError("Input files must be a list")

    def _validate_question_calculated_float(self, question, value, **kwargs):
        pass

    def validate(
        self,
        *,
        question,
        document,
        user,
        validation_context=None,
        instance=None,
        origin=False,
        data_source_context=None,
        **kwargs,
    ):
        # Check all possible fields for value
        value = None
        for i in ["documents", "files", "date", "value"]:
            value = kwargs.get(i, value)
            if value:
                break

        # empty values are allowed
        # required check will be done in DocumentValidator
        if value in EMPTY_VALUES:
            return

        validate_mapping = {
            "text": self._validate_question_text,
            "textarea": self._validate_question_textarea,
            "float": self._validate_question_float,
            "integer": self._validate_question_integer,
            "date": self._validate_question_date,
            "choice": self._validate_question_choice,
            "multiple_choice": self._validate_question_multiple_choice,
            "dynamic_choice": self._validate_question_dynamic_choice,
            "dynamic_multiple_choice": self._validate_question_dynamic_multiple_choice,
            "table": self._validate_question_table,
            "files": self._validate_question_files,
            "calculated_float": self._validate_question_calculated_float,
        }

        validate_func = validate_mapping[question.type]
        validate_func(
            question,
            value,
            document=document,
            user=user,
            validation_context=validation_context,
            instance=instance,
            origin=origin,
            data_source_context=data_source_context,
        )

        format_validators = get_format_validators(dic=True)
        for validator_slug in question.format_validators:
            format_validators[validator_slug].validate(value, document, question)


class DocumentValidator:
    def validate(
        self,
        document,
        user,
        validation_context=None,
        data_source_context=None,
        **kwargs,
    ):
        if not validation_context:
            validation_context = self.get_validation_context(document)

        required_but_empty = []

        all_fields = list(validation_context.get_all_fields())
        for field in all_fields:
            if field.is_required() and field.is_empty():
                required_but_empty.append(field)

        if required_but_empty:
            # When dealing with tables, the same question slug
            # might be missing multiple times. So we're normalizing a bit here
            affected_slugs = sorted(
                set([f.slug() for f in required_but_empty if f.slug()])
            )

            question_s, is_are = (
                ("Question", "is") if len(affected_slugs) == 1 else ("Questions", "are")
            )
            raise CustomValidationError(
                f"{question_s} {', '.join(affected_slugs)} "
                f"{is_are} required but not provided.",
                slugs=affected_slugs,
            )

        for field in all_fields:
            if field.is_visible() and field.answer:
                # if answer is not given, the required_but_empty check above would
                # already have raised an exception
                validator = AnswerValidator()
                validator.validate(
                    document=field.answer.document,
                    question=field.question,
                    value=field.answer.value,
                    documents=field.answer.documents.all(),
                    user=user,
                    validation_context=field,
                    data_source_context=data_source_context,
                )

    def get_validation_context(self, document, _fastloader=None):
        relevant_case: Case = (
            getattr(document, "case", None)
            or getattr(getattr(document, "work_item", None), "case", None)
            or None
        )

        case_form = (
            relevant_case.document.form_id
            if relevant_case and relevant_case.document
            else None
        )
        case_family_form = (
            relevant_case.family.document.form_id
            if relevant_case and relevant_case.family.document
            else None
        )
        case_info = (
            {
                # Why are we even represent this in context of the case?
                # The form does not belong there, it's not even there in
                # the model
                "form": case_form,
                "workflow": relevant_case.workflow_id,
                "root": {
                    "form": case_family_form,
                    "workflow": relevant_case.family.workflow_id,
                },
            }
            if relevant_case
            else None
        )
        workitem_info = (
            document.work_item.__dict__ if hasattr(document, "work_item") else None
        )
        context = {
            "info": {
                "document": document.family,
                "form": document.form,
                "case": case_info,
                "work_item": workitem_info,
            }
        }

        return structure.FieldSet(
            document,
            global_context=context,
            _fastloader=_fastloader,
        )

    def visible_questions(self, document, validation_context=None) -> list[Question]:
        """Evaluate the visibility of the questions for the given context.

        This evaluates the `is_hidden` expression for each question to decide
        if the question is visible.
        Return a list of question slugs that are visible.

        Note: If you pass in a validation context, it's the caller's
        responsibility to ensure it's the right one
        """
        if validation_context is None:
            validation_context = self.get_validation_context(document)

        return [
            field.question
            for field in validation_context.get_all_fields()
            if field.is_visible()
        ]


class QuestionValidator:
    @staticmethod
    def _validate_format_validators(data):
        format_validators = data.get("format_validators", [])
        if format_validators:
            fv = get_format_validators(include=format_validators, dic=True)

            for slug in format_validators:
                validator = fv.get(slug)

                if validator is None:
                    raise exceptions.ValidationError(
                        f"Invalid format validator {slug}."
                    )
                elif data["type"] not in validator.allowed_question_types:
                    raise exceptions.ValidationError(
                        f"Format validators {slug} is not allowed for this question type."
                    )

    @staticmethod
    def _validate_data_source(data_source):
        data_sources = get_data_sources(dic=True)
        if data_source not in data_sources:
            raise exceptions.ValidationError(f'Invalid data_source: "{data_source}"')

    @staticmethod
    def _validate_calc_expression(data):
        """Don't allow other calc questions or non-existent questions."""
        expr = data.get("calc_expression")
        if not expr:
            return

        question_jexl = jexl.QuestionJexl(field=None)
        deps = set(question_jexl.extract_referenced_questions(expr))

        inexistent_slugs = deps - set(
            models.Question.objects.filter(pk__in=deps).values_list("slug", flat=True)
        )
        illegal_deps = ", ".join(inexistent_slugs)

        if illegal_deps:  # pragma: no cover
            raise exceptions.ValidationError(
                f"Calc expression references inexistent questions: {illegal_deps}"
            )

    def validate(self, data):
        if data["type"] not in [
            models.Question.TYPE_ACTION_BUTTON,
            models.Question.TYPE_CALCULATED_FLOAT,
            models.Question.TYPE_STATIC,
            models.Question.TYPE_FORM,
        ]:
            self._validate_format_validators(data)
        elif data["type"] == models.Question.TYPE_CALCULATED_FLOAT:
            self._validate_calc_expression(data)

        if "dataSource" in data:
            self._validate_data_source(data["dataSource"])


def get_document_validity(document, user, **kwargs):
    validator = DocumentValidator()
    is_valid = True
    errors = []

    try:
        validator.validate(document, user, **kwargs)
    except CustomValidationError as exc:
        is_valid = False
        detail = str(exc.detail[0])
        errors = [{"slug": slug, "error_msg": detail} for slug in exc.slugs]

    return {"id": document.id, "is_valid": is_valid, "errors": errors}
