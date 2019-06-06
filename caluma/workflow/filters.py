from graphene import Enum

from ..core.filters import (
    FilterSet,
    GlobalIDFilter,
    HasAnswerFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    StringListFilter,
    generate_list_filter_class,
)
from . import models


def case_status_filter(*args, **kwargs):
    case_status_descriptions = {
        s.upper(): d for s, d in models.Case.STATUS_CHOICE_TUPLE
    }

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return case_status_descriptions[self.name]

    enum = Enum(
        "CaseStatusArgument",
        [(i.upper(), i) for i in models.Case.STATUS_CHOICES],
        type=EnumWithDescriptionsType,
    )
    return generate_list_filter_class(enum)(*args, **kwargs)


class WorkflowFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="WorkflowOrdering", fields=("name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


class FlowFilterSet(FilterSet):
    task = GlobalIDFilter(field_name="task_flows__task")

    class Meta:
        model = models.Flow
        fields = ("task",)


class CaseFilterSet(MetaFilterSet):
    order_by = OrderingFilter(label="CaseOrdering", fields=("status",))

    has_answer = HasAnswerFilter(document_id="document__pk")
    status = case_status_filter(lookup_expr="in")

    class Meta:
        model = models.Case
        fields = ("workflow",)


class TaskFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(
        label="TaskOrdering", fields=("name", "description", "type")
    )

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(MetaFilterSet):
    order_by = OrderingFilter(label="WorkItemOrdering", fields=("status", "deadline"))
    addressed_groups = StringListFilter(lookup_expr="overlap")

    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
