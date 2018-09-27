from rest_framework import exceptions

from . import models
from .. import serializers


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("form", "meta")


class AnswerSerializer(serializers.ModelSerializer):
    def validate_question_text(self, question, value):
        if not isinstance(value, str) or len(value) > question.max_length:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and max length {question.max_length}"
            )

    def validate_question_textarea(self, question, value):
        self.validate_question_text(question, value)

    def validate_question_float(self, question, value):
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

    def validate_question_integer(self, question, value):
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

    def validate_question_radio(self, question, value):
        options = question.options.values_list("slug", flat=True)
        if not isinstance(value, str) or value not in options:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and one of the options {'.'.join(options)}"
            )

    def validate_question_checkbox(self, question, value):
        options = question.options.values_list("slug", flat=True)
        invalid_options = set(value) - set(options)
        if not isinstance(value, list) or invalid_options:
            raise exceptions.ValidationError(
                f"Invalid options [{', '.join(invalid_options)}]. "
                f"Should be one of the options [{', '.join(options)}]"
            )

    def validate(self, data):
        question = data["question"]
        value = data["value"]
        getattr(self, f"validate_question_{question.type}")(question, value)

        return data

    class Meta:
        model = models.Answer
        fields = ("question", "meta", "document", "value")
