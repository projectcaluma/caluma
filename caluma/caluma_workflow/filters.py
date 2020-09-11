import graphene
from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import BooleanFilter

from ..caluma_core.filters import (
    CharFilter,
    FilterSet,
    GlobalIDFilter,
    JSONValueFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    SlugMultipleChoiceFilter,
    StringListFilter,
    generate_list_filter_class,
)
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from ..caluma_form.filters import HasAnswerFilter, SearchAnswersFilter
from ..caluma_form.models import Answer, Question
from ..caluma_form.ordering import AnswerValueOrdering
from . import models


def case_status_filter(*args, **kwargs):
    case_status_descriptions = {
        s.upper(): d for s, d in models.Case.STATUS_CHOICE_TUPLE
    }

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return case_status_descriptions[self.name]

    enum = graphene.Enum(
        "CaseStatusArgument",
        [(key.upper(), key) for (key, desc) in models.Case.STATUS_CHOICE_TUPLE],
        type=EnumWithDescriptionsType,
    )
    return generate_list_filter_class(enum)(*args, **kwargs)


class WorkflowFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="WorkflowOrdering", fields=("name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


class WorkflowOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Workflow,
        fields=[
            "allow_all_forms",
            "created_by_group",
            "created_by_user",
            "description",
            "is_archived",
            "is_published",
            "name",
            "slug",
        ],
    )

    class Meta:
        model = models.Workflow
        fields = ("meta", "attribute")


class FlowFilterSet(FilterSet):
    task = GlobalIDFilter(field_name="task_flows__task")

    class Meta:
        model = models.Flow
        fields = ("task",)


class CaseFilterSet(MetaFilterSet):
    id = GlobalIDFilter()
    order_by = OrderingFilter(label="CaseOrdering", fields=("status",))

    document_form = CharFilter(field_name="document__form_id")
    document_forms = SlugMultipleChoiceFilter(field_name="document__form_id")
    has_answer = HasAnswerFilter(document_id="document__pk")
    work_item_document_has_answer = HasAnswerFilter(
        document_id="work_items__document__pk"
    )
    root_case = GlobalIDFilter(field_name="family")
    search_answers = SearchAnswersFilter(document_id="document__pk")
    status = case_status_filter(lookup_expr="in")
    order_by_question_answer_value = CharFilter(
        method="filter_order_by_question_answer_value",
        label=(
            "Expects a question slug. If the slug is prefixed with a hyphen, "
            "the order will be reversed\n\n"
            "For file questions, the filename is used for sorting.\n\n"
            "Table questions are not supported at this time."
        ),
    )

    @staticmethod
    def filter_order_by_question_answer_value(queryset, _, question_slug):
        order_by = "-order_value" if question_slug.startswith("-") else "order_value"
        question_slug = question_slug.lstrip("-")

        # Based on question type, set answer field to use for sorting
        not_supported = (Question.TYPE_TABLE,)
        question = Question.objects.get(slug=question_slug)
        answer_value = "value"
        if question.type in not_supported:
            raise RuntimeError(
                f'Questions with type "{question.type}" are not supported '
                f'by "filterOrderByQuestionAnswerValue"'
            )
        elif question.type == Question.TYPE_DATE:
            answer_value = "date"
        elif question.type == Question.TYPE_FILE:
            answer_value = "file__name"

        # Initialize subquery
        answers = Answer.objects.filter(
            question=question, document=OuterRef("document")
        )

        # Annotate the cases in the queryset with the value of the answer of the given
        # question and order by it.
        return queryset.annotate(
            order_value=Subquery(answers.values(answer_value)[:1])
        ).order_by(order_by)

    class Meta:
        model = models.Case
        fields = ("workflow",)


class CaseOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Case,
        fields=[
            "allow_all_forms",
            "created_by_group",
            "created_by_user",
            "description",
            "is_archived",
            "is_published",
            "name",
            "status",
            "slug",
        ],
    )
    document_answer = AnswerValueOrdering(document_via="document")

    class Meta:
        model = models.Case
        fields = ("meta", "attribute", "document_answer")


class TaskFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(
        label="TaskOrdering", fields=("name", "description", "type")
    )

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class TaskOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.Task,
        fields=[
            "allow_all_forms",
            "lead_time",
            "type",
            "created_by_group",
            "created_by_user",
            "description",
            "is_archived",
            "is_published",
            "name",
            "slug",
        ],
    )

    class Meta:
        model = models.Task
        fields = ("meta", "attribute")


class WorkItemFilterSet(MetaFilterSet):
    id = GlobalIDFilter()
    order_by = OrderingFilter(label="WorkItemOrdering", fields=("status", "deadline"))
    addressed_groups = StringListFilter(lookup_expr="overlap")
    controlling_groups = StringListFilter(lookup_expr="overlap")
    assigned_users = StringListFilter(lookup_expr="overlap")

    document_has_answer = HasAnswerFilter(document_id="document__pk")
    case_document_has_answer = HasAnswerFilter(document_id="case__document__pk")
    case_meta_value = JSONValueFilter(field_name="case__meta")
    root_case_meta_value = JSONValueFilter(field_name="case__family__meta")

    tasks = SlugMultipleChoiceFilter(field_name="task_id")

    has_deadline = BooleanFilter(
        field_name="deadline", lookup_expr="isnull", exclude=True
    )
    case_family = GlobalIDFilter(field_name="case__family")

    class Meta:
        model = models.WorkItem
        fields = (
            "status",
            "name",
            "task",
            "tasks",
            "case",
            "created_at",
            "closed_at",
            "modified_at",
            "deadline",
            "has_deadline",
            "case_family",
        )


class WorkItemOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    case_meta = MetaFieldOrdering(field_name="case__meta")
    attribute = AttributeOrderingFactory(
        models.WorkItem,
        fields=[
            "allow_all_forms",
            "created_by_group",
            "created_by_user",
            "description",
            "created_at",
            "modified_at",
            "closed_at",
            "is_archived",
            "is_published",
            "name",
            "deadline",
            "status",
            "slug",
        ],
    )
    document_answer = AnswerValueOrdering(document_via="document")
    case_document_answer = AnswerValueOrdering(document_via="case__document")

    class Meta:
        model = models.WorkItem
        fields = (
            "meta",
            "case_meta",
            "attribute",
            "document_answer",
            "case_document_answer",
        )
