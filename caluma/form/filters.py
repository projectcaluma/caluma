from graphene_django.filter.filterset import GlobalIDMultipleChoiceFilter

from . import models
from ..filters import FilterSet, SearchFilter


class FormFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "is_published", "is_archived")


class QuestionFilterSet(FilterSet):
    exclude_forms = GlobalIDMultipleChoiceFilter(field_name="forms", exclude=True)
    search = SearchFilter(fields=("slug", "label", "type"))

    class Meta:
        model = models.Question
        fields = ("slug", "label", "type", "is_required", "is_hidden", "is_archived")
