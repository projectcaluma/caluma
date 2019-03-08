from . import models
from ..core.filters import (
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
)


class FormFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="FormOrdering", fields=("name",))

    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "is_published", "is_archived")


class OptionFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "label"))
    order_by = OrderingFilter(label="OptionOrdering", fields=("label",))

    class Meta:
        model = models.Option
        fields = ("slug", "label")


class QuestionFilterSet(MetaFilterSet):
    exclude_forms = GlobalIDMultipleChoiceFilter(field_name="forms", exclude=True)
    search = SearchFilter(fields=("slug", "label"))
    order_by = OrderingFilter(label="QuestionOrdering", fields=("label",))

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "is_archived")


class DocumentFilterSet(MetaFilterSet):
    id = GlobalIDFilter()
    search = SearchFilter(
        fields=("form__slug", "form__name", "form__description", "answers__value")
    )
    order_by = OrderingFilter(label="DocumentOrdering")

    class Meta:
        model = models.Document
        fields = ("form", "search", "id")


class AnswerFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("value",))
    order_by = OrderingFilter(label="AnswerOrdering")

    class Meta:
        model = models.Answer
        fields = ("question", "search")
