from graphene_django.filter.filterset import GlobalIDMultipleChoiceFilter

from . import models
from ..filters import FilterSet, SearchFilter


class FormSpecificationFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.FormSpecification
        fields = ("slug", "name", "description", "is_published", "is_archived")


class OptionFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "label"))

    class Meta:
        model = models.Option
        fields = ("slug", "label")


class QuestionFilterSet(FilterSet):
    exclude_form_specifications = GlobalIDMultipleChoiceFilter(
        field_name="form_specifications", exclude=True
    )
    search = SearchFilter(fields=("slug", "label"))

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "is_archived")


class FormFilterSet(FilterSet):
    search = SearchFilter(fields=("answers__value",))

    class Meta:
        model = models.Form
        fields = ("form_specification", "search")
