from . import models
from ..filters import FilterSet, SearchFilter


class WorkflowSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "is_published", "is_archived")


class WorkflowFilterSet(FilterSet):
    class Meta:
        model = models.Workflow
        fields = ("workflow_specification", "status")


class TaskSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.TaskSpecification
        fields = ("slug", "name", "description", "type", "is_archived")


class TaskFilterSet(FilterSet):
    class Meta:
        model = models.Task
        fields = ("status", "task_specification", "workflow")
