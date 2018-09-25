from rest_framework import exceptions

from . import models
from .. import serializers
from ..form.models import Question


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("form", "meta")


class AnswerSerializer(serializers.ModelSerializer):
    def validate(self, data):
        question = data["question"]
        value = data["value"]

        if question.type in (Question.TYPE_TEXT, Question.TYPE_TEXTAREA):
            if not isinstance(value, str) or len(value) > question.max_length:
                raise exceptions.ValidationError(
                    f"Invalid value {value}. "
                    f"Should be of type str and max length {question.max_length}"
                )
        elif question.type == Question.TYPE_FLOAT:
            if (
                not isinstance(value, float)
                or value < question.min_value
                or value > question.max_value
            ):
                raise exceptions.ValidationError(
                    f"Invalid value {value}. "
                    f"Should be of type float, not lower than {question.min_value} "
                    f"and not greater than {question.max_value}"
                )
        elif question.type == Question.TYPE_INTEGER:
            if (
                not isinstance(value, int)
                or value < question.min_value
                or value > question.max_value
            ):
                raise exceptions.ValidationError(
                    f"Invalid value {value}. "
                    f"Should be of type int, not lower than {question.min_value} "
                    f"and not greater than {question.max_value}"
                )

        return data

    class Meta:
        model = models.Answer
        fields = ("question", "meta", "document", "value")
