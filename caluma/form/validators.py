import sys

from rest_framework import exceptions

from . import jexl


class AnswerValidator:
    def _validate_question_text(self, question, value):
        max_length = (
            question.max_length if question.max_length is not None else sys.maxsize
        )
        if not isinstance(value, str) or len(value) > max_length:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and max length {max_length}"
            )

    def _validate_question_textarea(self, question, value):
        self.validate_question_text(question, value)

    def _validate_question_float(self, question, value):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, float) or value < min_value or value > max_value:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type float, not lower than {min_value} "
                f"and not greater than {max_value}"
            )

    def _validate_question_integer(self, question, value):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, int) or value < min_value or value > max_value:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type int, not lower than {min_value} "
                f"and not greater than {max_value}"
            )

    def _validate_question_radio(self, question, value):
        options = question.options.values_list("slug", flat=True)
        if not isinstance(value, str) or value not in options:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and one of the options {'.'.join(options)}"
            )

    def _validate_question_checkbox(self, question, value):
        options = question.options.values_list("slug", flat=True)
        invalid_options = set(value) - set(options)
        if not isinstance(value, list) or invalid_options:
            raise exceptions.ValidationError(
                f"Invalid options [{', '.join(invalid_options)}]. "
                f"Should be one of the options [{', '.join(options)}]"
            )

    def validate(self, *, question, value, **kwargs):
        # empty values are allowed
        # required check will be done in DocumentValidator
        if value:
            getattr(self, f"_validate_question_{question.type}")(question, value)


class DocumentValidator:
    def validate(self, *, form, answers, **kwargs):
        answers = answers.select_related("question").prefetch_related(
            "question__options"
        )
        answer_by_question = {answer.question.slug: answer.value for answer in answers}
        required_but_empty = []
        for question in form.questions.all():
            if jexl.QuestionJexl(answer_by_question).evaluate(question.is_required):
                if not answer_by_question.get(question.slug, None):
                    required_but_empty.append(question.slug)

        if required_but_empty:
            raise exceptions.ValidationError(
                f"Questions {','.join(required_but_empty)} are required but not provided."
            )

        for answer in answers:
            AnswerValidator().validate(question=answer.question, value=answer.value)
