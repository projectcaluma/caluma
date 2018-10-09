from . import models
from ..filters import FilterSet, SearchFilter


class WorkflowSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "is_published", "is_archived")


class CaseFilterSet(FilterSet):
    class Meta:
        model = models.Case
        fields = ("workflow_specification", "status")


class TaskFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(FilterSet):
    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
