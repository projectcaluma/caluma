import shlex
from functools import reduce

import graphene
from django.core import exceptions
from django.db import ProgrammingError
from django.db.models import F, Func, OuterRef, Q, Subquery
from django.forms import BooleanField
from django.utils import translation
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import Filter, FilterSet, MultipleChoiceFilter
from graphene import Enum, InputObjectType, List
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry
from rest_framework.exceptions import ValidationError

from ..caluma_core.filters import (
    CompositeFieldClass,
    GlobalIDFilter,
    GlobalIDMultipleChoiceFilter,
    MetaFilterSet,
    SearchFilter,
)
from ..caluma_core.forms import GlobalIDFormField
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from ..caluma_core.relay import extract_global_id
from ..caluma_form.models import Answer, DynamicOption, Form, Question, QuestionOption
from ..caluma_form.ordering import AnswerValueOrdering
from . import models, validators


class FormFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    slugs = MultipleChoiceFilter(field_name="slug")
    questions = MultipleChoiceFilter(field_name="questions__slug")

    class Meta:
        model = models.Form
        fields = (
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


class VisibleOptionFilter(Filter):
    """
    Filter options to only show ones whose `is_hidden` JEXL evaluates to false.

    This will make sure all the `is_hidden`-JEXLs on the options are evaluated in the
    context of the provided document.

    Note:
    This filter can only be used if the options in the QuerySet all belong only to
    one single question. Generally forms are built that way, but theoretically,
    options could be shared between questions. In that case it will throw a
    `ValidationError`.

    Also note that this evaluates JEXL for all the options of the question, which
    has a good bit of performance impact.

    """

    field_class = GlobalIDFormField

    def _validate(self, qs):
        # can't directly annotate, because the filter might already restrict to a
        # certain Question. In that case, the count would always be one
        questions = (
            QuestionOption.objects.filter(option_id=OuterRef("pk"))
            .order_by()
            .annotate(count=Func(F("pk"), function="Count"))
            .values("count")
        )

        qs = qs.annotate(num_questions=Subquery(questions)).annotate(
            question=F("questions")
        )

        if (
            qs.filter(num_questions__gt=1).exists()
            or len(set(qs.values_list("question", flat=True))) > 1
        ):
            raise ValidationError(
                "The `visibleInDocument`-filter can only be used if the filtered "
                "Options all belong to one unique question"
            )

    def filter(self, qs, value):
        if value in EMPTY_VALUES or not qs.exists():  # pragma: no cover
            return qs

        self._validate(qs)

        document_id = extract_global_id(value)

        # assuming qs can only ever be in the context of a single document
        document = models.Document.objects.get(pk=document_id)
        validator = validators.AnswerValidator()
        return qs.filter(
            slug__in=validator.visible_options(
                document, qs.first().questionoption_set.first().question, qs
            )
        )


class OptionFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "label"))
    visible_in_document = VisibleOptionFilter()

    class Meta:
        model = models.Option
        fields = ("slug", "label", "is_archived")


class OptionOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Option,
        fields=["created_at", "modified_at", "slug", "label", "is_archived"],
    )

    class Meta:
        model = models.Question
        fields = ("meta", "attribute")


class QuestionOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Question,
        fields=[
            "created_at",
            "modified_at",
            "slug",
            "label",
            "type",
            "is_required",
            "is_hidden",
            "is_archived",
            "placeholder",
            "info_text",
            "hint_text",
            "calc_expression",
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
        if value in EMPTY_VALUES:  # pragma: no cover
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
        # the converted type must be list-of-filter, as we need to apply
        # multiple conditions
        converted = List(HasAnswerFilterType)
        get_global_registry().register_converted_field(field, converted)
        return converted


class SearchLookupMode(Enum):
    """
    Lookup used in SearchAnswersFilterType.

    Keep in mind that the SearchAnswer filter operates on a word-by-word basis.
    This defines the lookup used for every single word.
    """

    STARTSWITH = "startswith"
    CONTAINS = "icontains"
    TEXT = "search"
    EXACT_WORD = "exact"


class SearchAnswersFilterType(InputObjectType):
    """
    Lookup type to search in answers.

    You may pass in a list of question slugs and/or a list of form slugs to define
    which answers to search. If you pass in one or more forms, answers to the
    questions in that form will be searched. If you pass in one or more question
    slugs, the corresponding answers are searched. If you pass both, a superset
    of both is searched (ie. they do not limit each other).
    """

    questions = List(graphene.ID)
    forms = List(graphene.ID)
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

    @staticmethod
    def _split(value):
        lex = shlex.shlex(value, posix=True)
        lex.whitespace_split = True
        lex.commenters = ""
        lex.quotes = '"'
        return [i.strip() for i in lex if i.strip()]

    def get_search_terms(self, value):
        value = value.replace("\x00", "")  # strip null characters
        try:
            return self._split(value)
        except ValueError as e:
            if e.args[0] == "No closing quotation":
                return self._split(f'{value}"')

    def filter(self, qs, value):
        if value in EMPTY_VALUES:  # pragma: no cover
            return qs

        assert isinstance(value, list)

        for val in value:
            if val in EMPTY_VALUES:  # pragma: no cover
                continue
            qs = self._apply_filter(qs, val)
        return qs

    def _get_questions(self, value):
        raw_questions = value.get("questions")
        raw_forms = value.get("forms")
        questions = Question.objects.none()

        if not raw_questions and not raw_forms:
            raise exceptions.ValidationError(
                '"forms" and/or "questions" parameter must be set'
            )

        if raw_questions:
            questions = self._validate_and_get_questions(raw_questions)

        if raw_forms:
            forms = self._validate_and_get_forms(raw_forms)
            form_questions = Form.get_all_questions(forms)
            # Combine querysets: All questions of the given forms, as well as the
            # explicitly-requested questions.
            questions = questions | form_questions.filter(
                type__in=self.FIELD_MAP.keys()
            )

        return questions

    def _apply_filter(self, qs, value):
        questions = self._get_questions(value)

        for word in self.get_search_terms(value["value"]):
            answers_with_word = self._answers_with_word(
                questions,
                word,
                value.get("lookup", SearchLookupMode.CONTAINS.value),
                value.get("forms"),
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

    def _answers_with_word(self, questions, word, lookup, form_slugs):
        if not questions:
            return Answer.objects.none()

        exprs = [
            self._word_lookup_for_question(question, word, lookup)
            for question in questions
        ]

        # join expressions with OR
        answer_qs = Answer.objects.filter(reduce(lambda a, b: a | b, exprs))

        # add form filter if given,
        # otherwise it would return all answers of the question filter ignoring the form filter
        if form_slugs not in EMPTY_VALUES:
            answer_qs = answer_qs.filter(document__form__pk__in=form_slugs)

        return answer_qs

    def _validate_and_get_questions(self, question_slugs):
        res = []
        for q_slug in question_slugs:
            question = Question.objects.get(pk=q_slug)
            if question.type not in self.FIELD_MAP:
                raise exceptions.ValidationError(
                    f"Questions of type {question.type} cannot be used in searchAnswers"
                )
            res.append(question)
        return Question.objects.filter(pk__in=res)

    @staticmethod
    def _validate_and_get_forms(form_slugs):
        forms = Form.objects.filter(slug__in=form_slugs)
        not_found = [
            x for x in form_slugs if x not in forms.values_list("slug", flat=True)
        ]
        if not_found:
            not_found_string = ", ".join(not_found)
            raise exceptions.ValidationError(
                f"Following forms could not be found: {not_found_string}"
            )
        return form_slugs

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
            "answers__files__name",
        )
    )
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
        models.Document, fields=["created_at", "modified_at", "form"]
    )

    class Meta:
        model = models.Document
        fields = ("meta", "answer_value", "attribute")


class VisibleAnswerFilter(Filter):
    field_class = BooleanField

    def filter(self, qs, value):
        if value in EMPTY_VALUES or not qs.exists():  # pragma: no cover
            # This prevents initializing the whole document structure with JEXL
            # computations if there is no value or no queryset to avoid useless
            # expensive computations
            return qs

        # assuming qs can only ever be in the context of a single document
        document = qs.first().document.family
        validator = validators.DocumentValidator()
        return qs.filter(question__slug__in=validator.visible_questions(document))


class VisibleQuestionFilter(Filter):
    field_class = GlobalIDFormField

    def filter(self, qs, value):
        if value in EMPTY_VALUES or not qs.exists():  # pragma: no cover
            return qs

        document_id = extract_global_id(value)

        # assuming qs can only ever be in the context of a single document
        document = models.Document.objects.get(pk=document_id)
        validator = validators.DocumentValidator()
        return qs.filter(slug__in=validator.visible_questions(document))


class QuestionFilterSet(MetaFilterSet):
    exclude_forms = GlobalIDMultipleChoiceFilter(field_name="forms", exclude=True)
    search = SearchFilter(fields=("slug", "label"))
    slugs = MultipleChoiceFilter(field_name="slug")

    visible_in_document = VisibleQuestionFilter()

    class Meta:
        model = models.Question
        fields = (
            "label",
            "is_required",
            "is_hidden",
            "is_archived",
            "sub_form",
            "row_form",
        )


class AnswerFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("value", "file__name"))
    questions = GlobalIDMultipleChoiceFilter(field_name="question")

    visible_in_context = VisibleAnswerFilter()

    class Meta:
        model = models.Answer
        fields = ("question", "search")


class AnswerOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Answer,
        fields=[
            "created_at",
            "modified_at",
            "question",
            "value",
            "date",
        ],
    )

    class Meta:
        model = models.Answer
        fields = ("meta", "attribute")


class DynamicOptionFilterSet(FilterSet):
    question = GlobalIDFilter()
    document = GlobalIDFilter()

    class Meta:
        model = models.DynamicOption
        fields = ("question", "document")


class DynamicOptionOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.DynamicOption,
        fields=["created_at", "modified_at", "slug", "label", "question"],
    )

    class Meta:
        model = models.DynamicOption
        fields = ("meta", "attribute")
