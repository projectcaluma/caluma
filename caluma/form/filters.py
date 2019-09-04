from functools import reduce

import graphene
from django import forms
from django.core import exceptions
from django.db import ProgrammingError
from django.db.models import Q
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import CharFilter, Filter
from graphene import Enum, InputObjectType, List
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry

from ..core.filters import (
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    SlugMultipleChoiceFilter,
)
from ..form.models import Answer, Question
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
        fields = ("slug", "label", "is_archived")


class QuestionFilterSet(MetaFilterSet):
    exclude_forms = GlobalIDMultipleChoiceFilter(field_name="forms", exclude=True)
    search = SearchFilter(fields=("slug", "label"))
    order_by = OrderingFilter(label="QuestionOrdering", fields=("label",))
    slugs = SlugMultipleChoiceFilter(field_name="slug")
    slug = CharFilter()
    slug.deprecation_reason = "Use the `slugs` (plural) filter instead, which allows filtering for multiple slugs"

    class Meta:
        model = models.Question
        fields = ("slug", "label", "is_required", "is_hidden", "is_archived")


class AnswerLookupMode(Enum):
    EXACT = "exact"
    STARTSWITH = "startswith"
    CONTAINS = "contains"
    ICONTAINS = "icontains"
    INTERSECTS = "intersects"

    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"


class AnswerHierarchyMode(Enum):
    DIRECT = "DIRECT"
    FAMILY = "FAMILY"


class HasAnswerFilterType(InputObjectType):
    """Lookup type to search document structures."""

    question = graphene.String(required=True)
    value = graphene.types.generic.GenericScalar(required=True)
    lookup = AnswerLookupMode()
    hierarchy = AnswerHierarchyMode()


class HasAnswerFilterField(forms.MultiValueField):
    def __init__(self, label, **kwargs):
        super().__init__(fields=(forms.CharField(), forms.CharField()))

    def clean(self, data):
        # override parent clean() which would reject our data structure.
        # We don't validate, as the structure is already enforced by the
        # schema.
        return data


class HasAnswerFilter(Filter):
    field_class = HasAnswerFilterField

    def __init__(self, *args, **kwargs):
        self.document_id = kwargs.pop("document_id")
        super().__init__(self, *args, **kwargs)

    VALID_LOOKUPS = {
        "text": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.STARTSWITH,
            AnswerLookupMode.CONTAINS,
            AnswerLookupMode.ICONTAINS,
        ],
        "integer": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.LT,
            AnswerLookupMode.LTE,
            AnswerLookupMode.GT,
            AnswerLookupMode.GTE,
        ],
        "multiple_choice": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.CONTAINS,
            AnswerLookupMode.INTERSECTS,
        ],
    }
    VALID_LOOKUPS["date"] = VALID_LOOKUPS["integer"]
    VALID_LOOKUPS["float"] = VALID_LOOKUPS["integer"]
    VALID_LOOKUPS["choice"] = VALID_LOOKUPS["multiple_choice"]
    VALID_LOOKUPS["dynamic_choice"] = VALID_LOOKUPS["multiple_choice"]
    VALID_LOOKUPS["dynamic_multiple_choice"] = VALID_LOOKUPS["multiple_choice"]
    VALID_LOOKUPS["textarea"] = VALID_LOOKUPS["text"]
    VALID_LOOKUPS["datetime"] = VALID_LOOKUPS["integer"]

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        for expr in value:
            qs = self.apply_expr(qs, expr)
        return qs

    def apply_expr(self, qs, expr):
        question_slug = expr["question"]
        match_value = expr["value"]

        lookup = expr.get("lookup", self.lookup_expr)
        hierarchy = expr.get("hierarchy", AnswerHierarchyMode.FAMILY)

        question = models.Question.objects.get(slug=question_slug)
        self._validate_lookup(question, lookup)

        answer_value = "value"
        if question.type == models.Question.TYPE_DATE:
            answer_value = "date"

        answers = models.Answer.objects.all()

        if lookup == AnswerLookupMode.INTERSECTS:
            inner_lookup = "exact"
            if question.type in (
                models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
                models.Question.TYPE_MULTIPLE_CHOICE,
            ):
                inner_lookup = "contains"

            exprs = [
                Q(**{f"value__{inner_lookup}": val, "question__slug": question_slug})
                for val in match_value
            ]
            # connect all expressions with OR
            answers = answers.filter(reduce(lambda a, b: a | b, exprs))
        else:
            answers = answers.filter(
                **{
                    f"{answer_value}__{lookup}": match_value,
                    "question__slug": question_slug,
                }
            )

        if hierarchy == AnswerHierarchyMode.FAMILY:
            return qs.filter(
                **{f"{self.document_id}__in": answers.values("document__family")}
            )
        else:
            return qs.filter(**{f"{self.document_id}__in": answers.values("document")})

    def _validate_lookup(self, question, lookup):
        try:
            valid_lookups = self.VALID_LOOKUPS[question.type]
        except KeyError:  # pragma: no cover
            # Not covered in tests - this only happens when you add a new
            # question type and forget to update the lookup config above.  In
            # that case, the fix is simple - go up a few lines and adjust the
            # VALID_LOOKUPS dict.
            raise ProgrammingError(
                f"Valid lookups not configured for question type {question.type}"
            )

        if lookup not in valid_lookups:
            raise exceptions.ValidationError(
                f"Invalid lookup for question slug={question.slug} ({question.type.upper()}): {lookup.upper()}"
            )

    @staticmethod
    @convert_form_field.register(HasAnswerFilterField)
    def convert_meta_value_field(field):
        registry = get_global_registry()
        converted = registry.get_converted_field(field)
        if converted:
            return converted

        # the converted type must be list-of-filter, as we need to apply
        # multiple conditions
        converted = List(HasAnswerFilterType)
        registry.register_converted_field(field, converted)
        return converted


class SearchLookupMode(Enum):
    STARTSWITH = "startswith"
    CONTAINS = "icontains"
    TEXT = "search"


class SearchAnswersFilterType(InputObjectType):
    """Lookup type to search in answers."""

    questions = List(graphene.String)
    value = graphene.types.generic.GenericScalar(required=True)
    lookup = SearchLookupMode(required=False)


class SearchAnswersFilterField(forms.MultiValueField):
    def __init__(self, label, **kwargs):
        super().__init__(fields=(forms.CharField(), forms.CharField()))

    def clean(self, data):
        # override parent clean() which would reject our data structure.
        # We don't validate, as the structure is already enforced by the
        # schema.
        return data


class SearchAnswersFilter(Filter):
    field_class = SearchAnswersFilterField

    FIELD_MAP = {
        Question.TYPE_TEXT: "value",
        Question.TYPE_TEXTAREA: "value",
        Question.TYPE_DATE: "date",
        Question.TYPE_CHOICE: "value",
        Question.TYPE_DYNAMIC_CHOICE: "value",
        Question.TYPE_INTEGER: "value",
        Question.TYPE_FLOAT: "value",
    }

    def __init__(self, *args, **kwargs):
        self.document_id = kwargs.pop("document_id")
        super().__init__(self, *args, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        assert isinstance(value, list)

        for val in value:
            if val in EMPTY_VALUES:  # pragma: no cover
                continue
            qs = self._apply_filter(qs, val)
        return qs

    def _apply_filter(self, qs, value):

        questions = self._validate_and_get_questions(value["questions"])

        for word in value["value"].split():
            answers_with_word = self._answers_with_word(
                questions, word, value.get("lookup", SearchLookupMode.CONTAINS.value)
            )
            qs = qs.filter(
                **{
                    f"{self.document_id}__in": answers_with_word.values(
                        "document__family"
                    )
                }
            )

        return qs

    def _answers_with_word(self, questions, word, lookup):
        exprs = [
            Q(
                **{
                    f"{self.FIELD_MAP[question.type]}__{lookup}": word,
                    "question": question,
                }
            )
            for q_slug, question in questions.items()
        ]

        # join expressions with OR
        return Answer.objects.filter(reduce(lambda a, b: a | b, exprs))

    def _validate_and_get_questions(self, questions):
        res = {}
        for q_slug in questions:
            question = Question.objects.get(pk=q_slug)
            if question.type not in self.FIELD_MAP:
                raise exceptions.ValidationError(
                    f"Questions of type {question.type} cannot be used in searchAnswers"
                )
            res[q_slug] = question
        return res

    @staticmethod
    @convert_form_field.register(SearchAnswersFilterField)
    def convert_meta_value_field(field):
        registry = get_global_registry()
        converted = registry.get_converted_field(field)
        if converted:
            return converted

        converted = List(SearchAnswersFilterType)
        registry.register_converted_field(field, converted)
        return converted


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
    search_answers = SearchAnswersFilter(document_id="pk")

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
