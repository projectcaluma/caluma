from . import models
from ..core.filters import (
    FilterSet,
    GlobalIDFilter,
    OrderingFilter,
    SearchFilter,
    StringListFilter,
)


class WorkflowFilterSet(FilterSet):
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


class CaseFilterSet(FilterSet):
    order_by = OrderingFilter(label="CaseOrdering", fields=("status",))

    class Meta:
        model = models.Case
        fields = ("workflow", "status")


class TaskFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(
        label="TaskOrdering", fields=("name", "description", "type")
    )

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(FilterSet):
    order_by = OrderingFilter(label="WorkItemOrdering", fields=("status",))
    addressed_groups = StringListFilter(lookup_expr="overlap")

    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
