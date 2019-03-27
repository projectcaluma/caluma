from ..core.filters import (
    AnswerValueFilter,
    FilterSet,
    GlobalIDFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    StringListFilter,
)
from . import models


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
    has_answer = AnswerValueFilter(answers_via="document__answers")

    class Meta:
        model = models.Case
        fields = ("workflow", "status", "has_answer")


class TaskFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(
        label="TaskOrdering", fields=("name", "description", "type")
    )

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(MetaFilterSet):
    order_by = OrderingFilter(label="WorkItemOrdering", fields=("status",))
    addressed_groups = StringListFilter(lookup_expr="overlap")

    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
