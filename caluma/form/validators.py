import sys
from logging import getLogger

from django_filters.constants import EMPTY_VALUES
from rest_framework import exceptions

from caluma.data_source.data_source_handlers import get_data_sources

from . import jexl
from .format_validators import get_format_validators
from .models import Answer, DynamicOption, Question

log = getLogger()


class CustomValidationError(exceptions.ValidationError):
    """Custom validation error to carry more information.

    This can carry more information about the error, so the documentValidity
    query can show more useful information.
    """

    def __init__(self, detail, code=None, slugs=None):
        slugs = slugs if slugs else []
        super().__init__(detail, code)
        self.slugs = slugs


class AnswerValidator:
    def _validate_question_text(self, question, value, **kwargs):
        max_length = (
            question.max_length if question.max_length is not None else sys.maxsize
        )
        if not isinstance(value, str) or len(value) > max_length:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and max length {max_length}",
                slugs=[question.slug],
            )

    def _validate_question_textarea(self, question, value, **kwargs):
        self._validate_question_text(question, value)

    def _validate_question_float(self, question, value, **kwargs):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, float) or value < min_value or value > max_value:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type float, not lower than {min_value} "
                f"and not greater than {max_value}",
                slugs=[question.slug],
            )

    def _validate_question_integer(self, question, value, **kwargs):
        min_value = (
            question.min_value if question.min_value is not None else float("-inf")
        )
        max_value = (
            question.max_value if question.max_value is not None else float("inf")
        )

        if not isinstance(value, int) or value < min_value or value > max_value:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type int, not lower than {min_value} "
                f"and not greater than {max_value}",
                slugs=[question.slug],
            )

    def _validate_question_date(self, question, value, **kwargs):
        pass

    def _validate_question_choice(self, question, value, **kwargs):
        options = question.options.values_list("slug", flat=True)
        if not isinstance(value, str) or value not in options:
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type str and one of the options {'.'.join(options)}",
                slugs=[question.slug],
            )

    def _validate_question_multiple_choice(self, question, value, **kwargs):
        options = question.options.values_list("slug", flat=True)
        invalid_options = set(value) - set(options)
        if not isinstance(value, list) or invalid_options:
            raise CustomValidationError(
                f"Invalid options [{', '.join(invalid_options)}]. "
                f"Should be one of the options [{', '.join(options)}]",
                slugs=[question.slug],
            )

    def _validate_question_dynamic_choice(
        self, question, value, document, info, **kwargs
    ):
        if not isinstance(value, str):
            raise CustomValidationError(
                f'Invalid value "{value}". Must be of type str.', slugs=[question.slug]
            )
        self._validate_dynamic_option(question, document, value, info)

    def _validate_dynamic_option(self, question, document, option, info):
        data_source = get_data_sources(dic=True)[question.data_source]
        data_source_object = data_source()

        valid_label = data_source_object.validate_answer_value(
            option, document, question, info
        )
        if valid_label is False:
            raise CustomValidationError(
                f'Invalid value "{option}". Not a valid option.', slugs=[question.slug]
            )

        DynamicOption.objects.get_or_create(
            document=document,
            question=question,
            slug=option,
            label=valid_label,
            created_by_user=info.context.user.username,
            created_by_group=info.context.user.group,
        )

    def _validate_question_dynamic_multiple_choice(
        self, question, value, document, info, **kwargs
    ):
        if not isinstance(value, list):
            raise CustomValidationError(
                f'Invalid value: "{value}". Must be of type list', slugs=[question.slug]
            )

        for v in value:
            if not isinstance(v, str):
                raise CustomValidationError(
                    f'Invalid value: "{v}". Must be of type string',
                    slugs=[question.slug],
                )
            self._validate_dynamic_option(question, document, v, info)

    def _validate_question_table(self, question, value, document, info, **kwargs):

        for _document in value:
            DocumentValidator().validate(_document, info=info, **kwargs)

    def _validate_question_file(self, question, value, **kwargs):
        pass

    def validate(self, *, question, document, info, validation_context=None, **kwargs):
        # Check all possible fields for value
        value = None
        for i in ["value", "file", "date", "documents"]:
            value = kwargs.get(i, value)
            if value:
                break

        # empty values are allowed
        # required check will be done in DocumentValidator
        if value:
            validate_func = getattr(self, f"_validate_question_{question.type}")
            validate_func(
                question,
                value,
                document=document,
                info=info,
                validation_context=validation_context,
            )

        format_validators = get_format_validators(dic=True)
        for validator_slug in question.format_validators:
            format_validators[validator_slug]().validate(value, document)


class DocumentValidator:
    def validate(self, document, info, validation_context=None, **kwargs):
        if not validation_context:
            validation_context = self._validation_context(document)

        for answer in document.answers.filter(
            question_id__in=self.visible_questions(document, validation_context)
        ):
            validator = AnswerValidator()
            validator.validate(
                document=document,
                question=answer.question,
                value=answer.value,
                documents=answer.documents.all(),
                info=info,
                validation_context=validation_context,
            )

    def _validation_context(self, document):
        all_questions = {q.slug: q for q in document.form.all_questions()}
        questions = {q.slug: q for q in document.form.questions.all()}
        return {
            "form": document.form,
            "document": document,
            "all_questions": all_questions,
            "questions": questions,
            "answers": self.get_document_answers(document),
        }

    def visible_questions(self, document, validation_context=None):
        if not validation_context:
            validation_context = self._validation_context(document)

        return self._validate_required(validation_context=validation_context)

    def get_document_answers(self, document):
        doc_answers = document.answers.select_related("question").prefetch_related(
            "question__options"
        )

        answers = {
            ans.question_id: self._get_answer_value(ans, document)
            for ans in doc_answers
        }

        # Create answer values for questions in the form that don't have
        # answers (yet)
        questions = document.form.all_questions().values("slug", "type")
        unanswered = {
            q["slug"]: self._get_answer_value(
                Answer(question_id=q["slug"], document=document), document
            )
            for q in questions
            if q["slug"] not in answers
            and q["type"] not in [Question.TYPE_FORM, Question.TYPE_STATIC]
        }

        answers.update(unanswered)
        return answers

    def _get_answer_value(self, answer, document):

        if answer.value is not None:
            return answer.value

        if answer.question.type in (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            Question.TYPE_MULTIPLE_CHOICE,
        ):
            # Unanswered multiple choice should return empty list
            # to denote emptyness
            return []

        elif answer.question.type == Question.TYPE_TABLE:
            # table type maps to list of dicts
            return [
                self.get_document_answers(document)
                for document in answer.documents.all()
            ]

        elif answer.question.type == Question.TYPE_FILE:
            if answer.file:
                return answer.file.name
        elif answer.question.type == Question.TYPE_DATE:
            return answer.date

        # Simple scalar types' value default to None in validation context
        elif answer.question.type in (
            Question.TYPE_INTEGER,
            Question.TYPE_FLOAT,
            Question.TYPE_TEXTAREA,
            Question.TYPE_TEXT,
            Question.TYPE_STATIC,
            Question.TYPE_DYNAMIC_CHOICE,
            Question.TYPE_CHOICE,
        ):
            return None

        else:  # pragma: no cover
            raise Exception(f"unhandled question type mapping {answer.question.type}")

    def _validate_required(self, validation_context):  # noqa: C901
        """Validate the 'requiredness' of the given answers.

        Raise exceptions if a required question is not answered.

        Since we're iterating and evaluating `is_hidden` as well for this
        purpose, we help our call site by returning a list of *non-hidden*
        question slugs.
        """
        required_but_empty = []
        visible_questions = []

        answers = validation_context["answers"]

        q_jexl = jexl.QuestionJexl(validation_context)
        for question in validation_context["questions"].values():
            try:
                expr = "is_hidden"
                is_hidden = q_jexl.is_hidden(question)

                if not is_hidden:
                    visible_questions.append(question.slug)
                    expr = "is_required"

                    is_required = q_jexl.is_required(question)
                    if is_required and answers.get(question.slug) in EMPTY_VALUES:
                        required_but_empty.append(question.slug)

                    if question.type == Question.TYPE_FORM:
                        # form questions's answers are still in the top level document
                        sub_context = {
                            **validation_context,
                            "form": question.sub_form,
                            "questions": {
                                q.slug: q for q in question.sub_form.questions.all()
                            },
                        }
                        visible_questions.extend(self._validate_required(sub_context))
                    elif question.type == Question.TYPE_TABLE and is_required:
                        # all_questions does not descend into table questions, so
                        # we need to extend the context here.
                        # We need to validate presence in at least one row, but only
                        # if the table question is required.
                        row_visibles = set()
                        row_context = {
                            **validation_context,
                            "questions": {
                                q.slug: q for q in question.row_form.all_questions()
                            },
                            "form": question.row_form,
                        }
                        for row in validation_context["answers"][question.slug]:
                            sub_context = {
                                **row_context,
                                "answers": {**validation_context["answers"], **row},
                            }
                            row_visibles.update(self._validate_required(sub_context))
                        # TODO are table row questions "visible questions"?
                        # in other words - do we need to add the row questions to the visible questions here?
                        visible_questions.extend(row_visibles)

            except (jexl.QuestionMissing, exceptions.ValidationError):
                raise
            except Exception as exc:
                expr_jexl = getattr(question, expr)

                log.error(
                    f"Error while evaluating {expr} expression on question {question.slug}: "
                    f"{expr_jexl}: {str(exc)}"
                )
                raise RuntimeError(
                    f"Error while evaluating '{expr}' expression on question {question.slug}: "
                    f"{expr_jexl}. The system log contains more information"
                )

        if required_but_empty:
            raise CustomValidationError(
                f"Questions {','.join(required_but_empty)} are required but not provided.",
                slugs=required_but_empty,
            )

        return visible_questions


class QuestionValidator:
    @staticmethod
    def _validate_format_validators(data):
        format_validators = data.get("format_validators")
        if format_validators:
            fv = get_format_validators(include=format_validators, dic=True)
            diff_list = list(set(format_validators) - set(fv))
            if diff_list:
                raise exceptions.ValidationError(
                    f"Invalid format validators {diff_list}."
                )

    @staticmethod
    def _validate_data_source(data_source):
        data_sources = get_data_sources(dic=True)
        if data_source not in data_sources:
            raise exceptions.ValidationError(f'Invalid data_source: "{data_source}"')

    def validate(self, data):
        if data["type"] in ["text", "textarea"]:
            self._validate_format_validators(data)
        if "dataSource" in data:
            self._validate_data_source(data["dataSource"])


def get_document_validity(document, info):
    validator = DocumentValidator()
    is_valid = True
    errors = []

    try:
        validator.validate(document, info)
    except CustomValidationError as exc:
        is_valid = False
        detail = str(exc.detail[0])
        errors = [{"slug": slug, "error_msg": detail} for slug in exc.slugs]

    return {"id": document.id, "is_valid": is_valid, "errors": errors}
