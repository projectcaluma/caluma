import graphene
from django_filters.rest_framework import BooleanFilter, MultipleChoiceFilter

from ..caluma_core.filters import (
    BaseFilterSet,
    CharFilter,
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    JSONValueFilter,
    MetaFilterSet,
    SearchFilter,
    StringListFilter,
    generate_list_filter_class,
)
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from ..caluma_form.filters import HasAnswerFilter, SearchAnswersFilter
from ..caluma_form.ordering import AnswerValueOrdering
from . import models


def case_status_filter(*args, **kwargs):
    case_status_descriptions = {
        s.upper(): d for s, d in models.Case.STATUS_CHOICE_TUPLE
    }

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return case_status_descriptions[self.name]

    enum = graphene.Enum(
        "CaseStatusArgument",
        [(key.upper(), key) for (key, desc) in models.Case.STATUS_CHOICE_TUPLE],
        type=EnumWithDescriptionsType,
    )
    return generate_list_filter_class(enum)(*args, **kwargs)


class WorkflowFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


class WorkflowOrderSet(BaseFilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Workflow,
        fields=[
            "created_at",
            "modified_at",
            "allow_all_forms",
            "description",
            "is_archived",
            "is_published",
            "name",
            "slug",
        ],
    )

    class Meta:
        model = models.Workflow
        fields = ("meta", "attribute")


class FlowFilterSet(BaseFilterSet):
    task = GlobalIDFilter(field_name="task_flows__task")

    class Meta:
        model = models.Flow
        fields = ("task",)


class FlowOrderSet(BaseFilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Flow,
        fields=["created_at", "modified_at", "task"],
    )

    class Meta:
        model = models.Flow
        fields = ("meta", "attribute")


class CaseFilterSet(MetaFilterSet):
    id = GlobalIDFilter()
    id.deprecation_reason = "Use ids filter instead"
    ids = GlobalIDMultipleChoiceFilter(field_name="pk")

    document_form = CharFilter(field_name="document__form_id")
    document_forms = MultipleChoiceFilter(field_name="document__form_id")
    has_answer = HasAnswerFilter(document_id="document__pk")
    work_item_document_has_answer = HasAnswerFilter(
        document_id="work_items__document__pk"
    )
    root_case = GlobalIDFilter(field_name="family")
    search_answers = SearchAnswersFilter(document_id="document__pk")
    status = case_status_filter(lookup_expr="in")
    exclude_child_cases = BooleanFilter(method="filter_exclude_child_cases")

    def filter_exclude_child_cases(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(parent_work_item__isnull=True)

    class Meta:
        model = models.Case
        fields = ("workflow",)


class CaseOrderSet(BaseFilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Case,
        fields=[
            "created_at",
            "modified_at",
            "status",
            "document__form__name",
        ],
    )
    document_answer = AnswerValueOrdering(document_via="document")

    class Meta:
        model = models.Case
        fields = ("meta", "attribute", "document_answer")


class TaskFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class TaskOrderSet(BaseFilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Task,
        fields=[
            "created_at",
            "modified_at",
            "lead_time",
            "type",
            "description",
            "is_archived",
            "name",
            "slug",
        ],
    )

    class Meta:
        model = models.Task
        fields = ("meta", "attribute")


class WorkItemFilterSet(MetaFilterSet):
    id = GlobalIDFilter()
    addressed_groups = StringListFilter(lookup_expr="overlap")
    controlling_groups = StringListFilter(lookup_expr="overlap")
    assigned_users = StringListFilter(lookup_expr="overlap")

    document_has_answer = HasAnswerFilter(document_id="document__pk")
    case_document_has_answer = HasAnswerFilter(document_id="case__document__pk")
    case_meta_value = JSONValueFilter(field_name="case__meta")
    root_case_meta_value = JSONValueFilter(field_name="case__family__meta")
    case_search_answers = SearchAnswersFilter(document_id="case__document__pk")

    tasks = MultipleChoiceFilter(field_name="task_id")

    has_deadline = BooleanFilter(
        field_name="deadline", lookup_expr="isnull", exclude=True
    )
    case_family = GlobalIDFilter(field_name="case__family")

    class Meta:
        model = models.WorkItem
        fields = (
            "status",
            "name",
            "task",
            "tasks",
            "case",
            "created_at",
            "closed_at",
            "modified_at",
            "deadline",
            "has_deadline",
            "case_family",
        )


class WorkItemOrderSet(BaseFilterSet):
    meta = MetaFieldOrdering()
    case_meta = MetaFieldOrdering(field_name="case__meta")
    attribute = AttributeOrderingFactory(
        models.WorkItem,
        fields=[
            "created_at",
            "modified_at",
            "closed_at",
            "description",
            "name",
            "deadline",
            "status",
            "slug",
            "case__document__form__name",
        ],
    )
    document_answer = AnswerValueOrdering(document_via="document")
    case_document_answer = AnswerValueOrdering(document_via="case__document")

    class Meta:
        model = models.WorkItem
        fields = (
            "meta",
            "case_meta",
            "attribute",
            "document_answer",
            "case_document_answer",
        )
