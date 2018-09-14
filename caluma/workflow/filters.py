from . import models
from ..filters import FilterSet, SearchFilter


class WorkflowSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "is_published", "is_archived")


class TaskSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.TaskSpecification
        fields = ("slug", "name", "description", "type", "is_archived")
