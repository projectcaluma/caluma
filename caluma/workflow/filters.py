from . import models
from ..core.filters import FilterSet, OrderingFilter, SearchFilter


class WorkflowFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="WorkflowOrdering", fields=("name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


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

    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
