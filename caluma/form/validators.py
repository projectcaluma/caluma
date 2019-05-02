import sys

from rest_framework import exceptions

from caluma.data_source.data_source_handlers import (
    get_data_source_data,
    get_data_sources,
)

from . import jexl
from .models import Question


class AnswerValidator:
    def _validate_question_text(self, question, value, **kwargs):
        max_length = (
            question.max_length if question.max_length is not None else sys.maxsize
        )
        if not isinstance(value, str) or len(value) > max_length:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and max length {max_length}"
            )

    def _validate_question_textarea(self, question, value, **kwargs):
        self._validate_question_text(question, value)

    def _validate_question_float(self, question, value, document, **kwargs):
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

    def _validate_question_integer(self, question, value, **kwargs):
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

    def _validate_question_date(self, question, value, **kwargs):
        pass

    def _validate_question_choice(self, question, value, **kwargs):
        options = question.options.values_list("slug", flat=True)
        if not isinstance(value, str) or value not in options:
            raise exceptions.ValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and one of the options {'.'.join(options)}"
            )

    def _validate_question_multiple_choice(self, question, value, **kwargs):
        options = question.options.values_list("slug", flat=True)
        invalid_options = set(value) - set(options)
        if not isinstance(value, list) or invalid_options:
            raise exceptions.ValidationError(
                f"Invalid options [{', '.join(invalid_options)}]. "
                f"Should be one of the options [{', '.join(options)}]"
            )

    def _validate_question_dynamic_choice(self, question, value, info, **kwargs):
        data_source = get_data_sources(dic=True)[question.data_source]
        if not data_source.validate:
            if not isinstance(value, str):
                raise exceptions.ValidationError(
                    f'Invalid value: "{value}". Must be of type str'
                )
            return

        data = get_data_source_data(info, question.data_source)
        options = [d.slug for d in data]

        if not isinstance(value, str) or value not in options:
            raise exceptions.ValidationError(
                f'Invalid value "{value}". '
                f"Must be of type str and one of the options \"{', '.join(options)}\""
            )

    def _validate_question_dynamic_multiple_choice(
        self, question, value, info, **kwargs
    ):
        data_source = get_data_sources(dic=True)[question.data_source]
        if not data_source.validate:
            if not isinstance(value, list):
                raise exceptions.ValidationError(
                    f'Invalid value: "{value}". Must be of type list'
                )
            for v in value:
                if not isinstance(v, str):
                    raise exceptions.ValidationError(
                        f'Invalid value: "{v}". Must be of type string'
                    )
            return
        data = get_data_source_data(info, question.data_source)
        options = [d.slug for d in data]
        if not isinstance(value, list):
            raise exceptions.ValidationError(
                f'Invalid value: "{value}". Must be of type list'
            )
        invalid_options = set(value) - set(options)
        if invalid_options:
            raise exceptions.ValidationError(
                f'Invalid options "{invalid_options}". '
                f"Should be one of the options \"[{', '.join(options)}]\""
            )

    def _validate_question_table(self, question, value, document, info, **kwargs):
        for _document in value:
            DocumentValidator().validate(_document, parent=document, info=info)

    def _validate_question_form(self, question, value, document, info, **kwargs):
        DocumentValidator().validate(value, parent=document, info=info)

    def _validate_question_file(self, question, value, **kwargs):
        pass

    def validate(self, *, question, document, info, **kwargs):
        # Check all possible fields for value
        value = None
        for i in ["value", "file", "date", "documents", "value_document"]:
            value = kwargs.get(i, value)
            if value:
                break

        # empty values are allowed
        # required check will be done in DocumentValidator
        if value:
            getattr(self, f"_validate_question_{question.type}")(
                question, value, document=document, info=info
            )


class DocumentValidator:
    def validate(self, document, info, **kwargs):
        def get_answers_by_question(document):
            answers = document.answers.select_related("question").prefetch_related(
                "question__options"
            )
            return {
                answer.question.slug: self.get_answer_value(answer, document)
                for answer in answers
            }

        answer_by_question = get_answers_by_question(document)
        parent = kwargs.get("parent", None)
        if parent:
            answer_by_question["parent"] = get_answers_by_question(parent)

        self.validate_required(document, answer_by_question)

        for answer in document.answers.all():
            AnswerValidator().validate(
                document=document,
                question=answer.question,
                value=answer.value,
                value_document=answer.value_document,
                info=info,
            )

    def get_answer_value(self, answer, document):
        def get_document_answers(document):
            return {
                answer.question.pk: self.get_answer_value(answer, document)
                for answer in document.answers.all()
            }

        if answer.value is None:
            if answer.question.type == Question.TYPE_FORM:
                # form type maps to dict
                return get_document_answers(answer.value_document)

            elif answer.question.type == Question.TYPE_TABLE:
                # table type maps to list of dicts
                return [
                    get_document_answers(document)
                    for document in answer.documents.all()
                ]

            elif answer.question.type == Question.TYPE_FILE:
                return answer.file.name

            elif answer.question.type == Question.TYPE_DATE:
                return answer.date

            else:  # pragma: no cover
                raise Exception(
                    f"unhandled question type mapping {answer.question.type}"
                )

        return answer.value

    def validate_required(self, document, answer_by_question):
        required_but_empty = []
        for question in document.form.questions.all():
            if jexl.QuestionJexl(answer_by_question).evaluate(
                question.is_required
            ) and not jexl.QuestionJexl(answer_by_question).evaluate(
                question.is_hidden
            ):
                if not answer_by_question.get(question.slug, None):
                    required_but_empty.append(question.slug)

        if required_but_empty:
            raise exceptions.ValidationError(
                f"Questions {','.join(required_but_empty)} are required but not provided."
            )
