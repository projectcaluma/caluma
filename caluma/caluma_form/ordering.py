from typing import Any, Tuple

from django import forms
from django.db.models import OuterRef, Subquery
from django.db.models.expressions import F
from django.db.models.query import QuerySet
from rest_framework import exceptions

from caluma.caluma_core.ordering import CalumaOrdering, OrderingFieldType
from caluma.caluma_form.models import Answer, Question


class AnswerValueOrdering(CalumaOrdering):
    """Ordering filter for ordering documents by value of an answer.

    This can also be used for ordering other things that contain documents,
    such as cases, work items etc.
    """

    field_class = forms.CharField

    def __init__(self, document_via=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._document_locator_prefix = (
            "" if document_via is None else f"{document_via}__"
        )

    def get_ordering_value(
        self, qs: QuerySet, value: Any
    ) -> Tuple[QuerySet, OrderingFieldType]:
        # First, join the requested answer, then annotate the QS accordingly.
        # Last, return a field corresponding to the value
        #
        question = Question.objects.get(pk=value)
        QUESTION_TYPE_TO_FIELD = {
            Question.TYPE_INTEGER: "value",
            Question.TYPE_FLOAT: "value",
            Question.TYPE_DATE: "date",
            Question.TYPE_CHOICE: "value",
            Question.TYPE_TEXTAREA: "value",
            Question.TYPE_TEXT: "value",
            Question.TYPE_FILE: "file",
            Question.TYPE_DYNAMIC_CHOICE: "value",
            Question.TYPE_STATIC: "value",
        }

        try:
            value_field = QUESTION_TYPE_TO_FIELD[question.type]
        except KeyError:  # pragma: no cover
            raise exceptions.ValidationError(
                f"Question '{question.slug}' has unsupported type {question.type} for ordering"
            )

        answers_subquery = Subquery(
            Answer.objects.filter(
                question=question,
                document=OuterRef(f"{self._document_locator_prefix}pk"),
            ).values(value_field)
        )
        ann_name = f"order_{value}"

        qs = qs.annotate(**{ann_name: answers_subquery})

        # TODO: respect document_via
        return qs, F(ann_name)
