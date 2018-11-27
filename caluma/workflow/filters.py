from . import models
from ..core.filters import FilterSet, SearchFilter


class WorkflowFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


class CaseFilterSet(FilterSet):
    class Meta:
        model = models.Case
        fields = ("workflow", "status")


class TaskFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(FilterSet):
    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
