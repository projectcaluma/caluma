from django.db.models import OuterRef, Subquery
from graphene import Enum

from ..core.filters import (
    CharFilter,
    FilterSet,
    GlobalIDFilter,
    MetaFilterSet,
    OrderingFilter,
    SearchFilter,
    StringListFilter,
    generate_list_filter_class,
)
from ..form.filters import HasAnswerFilter
from ..form.models import Answer, Question
from . import models


def case_status_filter(*args, **kwargs):
    case_status_descriptions = {
        s.upper(): d for s, d in models.Case.STATUS_CHOICE_TUPLE
    }

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return case_status_descriptions[self.name]

    enum = Enum(
        "CaseStatusArgument",
        [(i.upper(), i) for i in models.Case.STATUS_CHOICES],
        type=EnumWithDescriptionsType,
    )
    return generate_list_filter_class(enum)(*args, **kwargs)


class WorkflowFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(label="WorkflowOrdering", fields=("name", "description"))

    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "is_published", "is_archived")


class FlowFilterSet(FilterSet):
    task = GlobalIDFilter(field_name="task_flows__task")

    class Meta:
        model = models.Flow
        fields = ("task",)


class CaseFilterSet(MetaFilterSet):
    order_by = OrderingFilter(label="CaseOrdering", fields=("status",))

    document_form = CharFilter(field_name="document__form_id")
    has_answer = HasAnswerFilter(document_id="document__pk")
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


class TaskFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    order_by = OrderingFilter(
        label="TaskOrdering", fields=("name", "description", "type")
    )

    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type", "is_archived")


class WorkItemFilterSet(MetaFilterSet):
    order_by = OrderingFilter(label="WorkItemOrdering", fields=("status", "deadline"))
    addressed_groups = StringListFilter(lookup_expr="overlap")

    document_has_answer = HasAnswerFilter(document_id="document__pk")
    case_document_has_answer = HasAnswerFilter(document_id="case__document__pk")

    class Meta:
        model = models.WorkItem
        fields = ("status", "task", "case")
