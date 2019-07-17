from django_filters.rest_framework import CharFilter

from ..core.filters import (
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    HasAnswerFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    SlugMultipleChoiceFilter,
)
from . import models


class FormFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="FormOrdering", fields=("name",))
    slugs = SlugMultipleChoiceFilter(field_name="slug")
    slug = CharFilter()
    slug.deprecation_reason = "Use the `slugs` (plural) filter instead, which allows filtering for multiple slugs"

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
        fields=(
            "form__slug",
            "form__name",
            "form__description",
            "answers__value",
            "answers__file__name",
        )
    )
    order_by = OrderingFilter(label="DocumentOrdering")
    root_document = GlobalIDFilter(field_name="family")
    forms = GlobalIDMultipleChoiceFilter(field_name="form")

    has_answer = HasAnswerFilter(document_id="pk")

    class Meta:
        model = models.Document
        fields = ("form", "forms", "search", "id")


class AnswerFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("value", "file__name"))
    order_by = OrderingFilter(label="AnswerOrdering")
    questions = GlobalIDMultipleChoiceFilter(field_name="question")

    class Meta:
        model = models.Answer
        fields = ("question", "search")
