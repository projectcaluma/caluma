from functools import reduce

import graphene
from django.core import exceptions
from django.db import ProgrammingError
from django.db.models import Q
from django.forms import BooleanField
from django.utils import translation
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import CharFilter, Filter, FilterSet
from graphene import Enum, InputObjectType, List
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry

from ..caluma_core.filters import (
    CompositeFieldClass,
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    SlugMultipleChoiceFilter,
)
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from ..caluma_form.models import Answer, DynamicOption, Question
from ..caluma_form.ordering import AnswerValueOrdering
from . import models, validators


class FormFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="FormOrdering", fields=("name",))
    slugs = SlugMultipleChoiceFilter(field_name="slug")
    slug = CharFilter()
    slug.deprecation_reason = "Use the `slugs` (plural) filter instead, which allows filtering for multiple slugs"
    questions = SlugMultipleChoiceFilter(field_name="questions__slug")

    class Meta:
        model = models.Form
        fields = (
            "slug",
            "name",
            "description",
            "is_published",
            "is_archived",
            "questions",
        )


class FormOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Form,
        fields=[
            "created_at",
            "modified_at",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
            "slug",
            "name",
            "description",
            "is_published",
            "is_archived",
        ],
    )

    class Meta:
        model = models.Form
        fields = ("meta", "attribute")


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
        fields = (
            "slug",
            "label",
            "is_required",
            "is_hidden",
            "is_archived",
            "sub_form",
            "row_form",
        )


class QuestionOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Question,
        exclude_fields=[
            "configuration",
            "data_source",
            "format_validators",
            "meta",
            "row_form",
            "source",
            "static_content",
            "sub_form",
            "default_answer",
            "calc_dependents",
        ],
    )

    class Meta:
        model = models.Question
        fields = ("meta", "attribute")


class AnswerLookupMode(Enum):
    EXACT = "exact"
    STARTSWITH = "startswith"
    CONTAINS = "contains"
    ICONTAINS = "icontains"
    INTERSECTS = "intersects"
    ISNULL = "isnull"
    IN = "in"

    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"


class AnswerHierarchyMode(Enum):
    DIRECT = "DIRECT"
    FAMILY = "FAMILY"


class HasAnswerFilterType(InputObjectType):
    """
    Lookup type to search document structures.

    When using lookup `ISNULL`, the provided `value` will be ignored.
    """

    question = graphene.ID(required=True)
    value = graphene.types.generic.GenericScalar(required=False)
    lookup = AnswerLookupMode()
    hierarchy = AnswerHierarchyMode()


class HasAnswerFilterField(CompositeFieldClass):
    pass


class HasAnswerFilter(Filter):
    field_class = HasAnswerFilterField

    def __init__(self, *args, **kwargs):
        self.document_id = kwargs.pop("document_id")
        super().__init__(*args, **kwargs)

    VALID_LOOKUPS = {
        "text": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.STARTSWITH,
            AnswerLookupMode.CONTAINS,
            AnswerLookupMode.ICONTAINS,
            AnswerLookupMode.ISNULL,
            AnswerLookupMode.IN,
        ],
        "integer": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.LT,
            AnswerLookupMode.LTE,
            AnswerLookupMode.GT,
            AnswerLookupMode.GTE,
            AnswerLookupMode.ISNULL,
            AnswerLookupMode.IN,
        ],
        "choice": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.IN,
            AnswerLookupMode.ISNULL,
        ],
        "multiple_choice": [
            AnswerLookupMode.EXACT,
            AnswerLookupMode.CONTAINS,
            AnswerLookupMode.INTERSECTS,
            AnswerLookupMode.ISNULL,
        ],
    }
    VALID_LOOKUPS["date"] = VALID_LOOKUPS["integer"]
    VALID_LOOKUPS["float"] = VALID_LOOKUPS["integer"]
    VALID_LOOKUPS["dynamic_choice"] = VALID_LOOKUPS["choice"]
    VALID_LOOKUPS["dynamic_multiple_choice"] = VALID_LOOKUPS["multiple_choice"]
    VALID_LOOKUPS["textarea"] = VALID_LOOKUPS["text"]
    VALID_LOOKUPS["datetime"] = VALID_LOOKUPS["integer"]
    VALID_LOOKUPS["calculated_float"] = VALID_LOOKUPS["float"]

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        for expr in value:
            qs = self.apply_expr(qs, expr)
        return qs

    def apply_expr(self, qs, expr):
        lookup = expr.get("lookup", self.lookup_expr)
        lookup_expr = (hasattr(lookup, "value") and lookup.value) or lookup

        question_slug = expr["question"]
        match_value = expr.get("value")
        if lookup == AnswerLookupMode.ISNULL:
            match_value = True

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
                    f"{answer_value}__{lookup_expr}": match_value,
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
            lookup = (hasattr(lookup, "value") and lookup.value) or lookup
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

    questions = List(graphene.ID)
    value = graphene.types.generic.GenericScalar(required=True)
    lookup = SearchLookupMode(required=False)


class SearchAnswersFilterField(CompositeFieldClass):
    pass


class SearchAnswersFilter(Filter):
    field_class = SearchAnswersFilterField

    FIELD_MAP = {
        Question.TYPE_TEXT: "value",
        Question.TYPE_TEXTAREA: "value",
        Question.TYPE_DATE: "date",
        Question.TYPE_CHOICE: "value",
        Question.TYPE_MULTIPLE_CHOICE: "value",
        Question.TYPE_DYNAMIC_CHOICE: "value",
        Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: "value",
        Question.TYPE_INTEGER: "value",
        Question.TYPE_FLOAT: "value",
    }

    def __init__(self, *args, **kwargs):
        self.document_id = kwargs.pop("document_id")
        super().__init__(*args, **kwargs)

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

    def _word_lookup_for_question(self, question, word, lookup):
        if question.type not in (
            Question.TYPE_CHOICE,
            Question.TYPE_DYNAMIC_CHOICE,
            Question.TYPE_MULTIPLE_CHOICE,
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        ):
            return Q(
                **{
                    f"{self.FIELD_MAP[question.type]}__{lookup}": word,
                    "question": question,
                }
            )

        # (Multiple) choice lookups need more specific treatment...
        lang = translation.get_language()
        is_multiple = question.type in (
            Question.TYPE_MULTIPLE_CHOICE,
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        )
        is_dynamic = question.type in (
            Question.TYPE_DYNAMIC_CHOICE,
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        )

        # find all options of our given question that match the
        # word, then use their slugs for lookup
        if is_dynamic:
            matching_options = (
                DynamicOption.objects.all()
                .filter(question=question, **{f"label__{lang}__{lookup}": word})
                .values_list("slug", flat=True)
            )
        else:
            matching_options = question.options.filter(
                **{f"label__{lang}__{lookup}": word}
            ).values_list("slug", flat=True)

        if not matching_options:
            # no labels = no results
            return Q(value=False) & Q(value=True)

        filt = "value__contains" if is_multiple else "value"
        return reduce(
            lambda a, b: a | b, [Q(**{filt: slug}) for slug in matching_options]
        )

    def _answers_with_word(self, questions, word, lookup):
        exprs = [
            self._word_lookup_for_question(question, word, lookup)
            for q_slug, question in questions.items()
        ]

        # join expressions with OR
        answer_qs = Answer.objects.filter(reduce(lambda a, b: a | b, exprs))
        return answer_qs

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
            # TODO: can this be removed, as it's never the case
            # anymore with graphene 3.0?
            # Doesn't seem to have ill effects...
            return converted  # pragma: no cover

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


class DocumentOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    answer_value = AnswerValueOrdering()
    attribute = AttributeOrderingFactory(
        models.Document, exclude_fields=["meta", "family", "id"]
    )

    class Meta:
        model = models.Document
        fields = ("meta",)


class VisibleAnswerFilter(Filter):
    field_class = BooleanField

    def filter(self, qs, value):
        if not value or not qs.exists():
            return qs

        # assuming qs can only ever be in the context of a single document
        document = qs.first().document.family
        validator = validators.DocumentValidator()
        return qs.filter(question__slug__in=validator.visible_questions(document))


class AnswerFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("value", "file__name"))
    order_by = OrderingFilter(label="AnswerOrdering")
    questions = GlobalIDMultipleChoiceFilter(field_name="question")

    visible_in_context = VisibleAnswerFilter()

    class Meta:
        model = models.Answer
        fields = ("question", "search")


class AnswerOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(models.Answer, exclude_fields=["meta", "id"])

    class Meta:
        model = models.Answer
        fields = ("meta",)


class DynamicOptionFilterSet(FilterSet):
    question = GlobalIDFilter()
    document = GlobalIDFilter()

    class Meta:
        model = models.DynamicOption
        fields = ("question", "document")
