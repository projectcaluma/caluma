from . import models
from ..filters import (
    FilterSet,
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    SearchFilter,
)


class FormFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))

    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "is_published", "is_archived")


class OptionFilterSet(FilterSet):
    search = SearchFilter(fields=("slug", "label"))

    class Meta:
        model = models.Option
        fields = ("slug", "label")


class QuestionFilterSet(FilterSet):
    exclude_forms = GlobalIDMultipleChoiceFilter(field_name="forms", exclude=True)
    search = SearchFilter(fields=("slug", "label"))

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "is_archived")


class DocumentFilterSet(FilterSet):
    id = GlobalIDFilter()
    search = SearchFilter(
        fields=("form__slug", "form__name", "form__description", "answers__value")
    )

    class Meta:
        model = models.Document
        fields = ("form", "search", "id")


class AnswerFilterSet(FilterSet):
    search = SearchFilter(fields=("value",))

    class Meta:
        model = models.Answer
        fields = ("question", "search")
