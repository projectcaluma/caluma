import sys
from collections import defaultdict
from logging import getLogger

from django_filters.constants import EMPTY_VALUES
from rest_framework import exceptions

from caluma.caluma_data_source.data_source_handlers import get_data_sources

from . import jexl, structure
from .format_validators import get_format_validators
from .models import DynamicOption, Question

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
        min_length = question.min_length if question.min_length is not None else 0
        max_length = (
            question.max_length if question.max_length is not None else sys.maxsize
        )

        if (
            not isinstance(value, str)
            or len(value) < min_length
            or len(value) > max_length
        ):
            raise CustomValidationError(
                f"Invalid value {value}. "
                f"Should be of type str, and it's length between {min_length} and {max_length}",
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
        self, question, value, document, user, **kwargs
    ):
        if not isinstance(value, str):
            raise CustomValidationError(
                f'Invalid value "{value}". Must be of type str.', slugs=[question.slug]
            )
        self._validate_dynamic_option(question, document, value, user)

    def _validate_dynamic_option(self, question, document, option, user):
        data_source = get_data_sources(dic=True)[question.data_source]
        data_source_object = data_source()

        valid_label = data_source_object.validate_answer_value(
            option, document, question, user
        )
        if valid_label is False:
            raise CustomValidationError(
                f'Invalid value "{option}". Not a valid option.', slugs=[question.slug]
            )

        DynamicOption.objects.get_or_create(
            document=document,
            question=question,
            slug=option,
            defaults={
                "label": valid_label,
                "created_by_user": user.username,
                "created_by_group": user.group,
            },
        )

    def _validate_question_dynamic_multiple_choice(
        self, question, value, document, user, **kwargs
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
            self._validate_dynamic_option(question, document, v, user)

    def _validate_question_table(self, question, value, document, user, **kwargs):

        for row_doc in value:
            DocumentValidator().validate(row_doc, user=user, **kwargs)

    def _validate_question_file(self, question, value, **kwargs):
        pass

    def validate(self, *, question, document, user, validation_context=None, **kwargs):
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
                user=user,
                validation_context=validation_context,
            )

        format_validators = get_format_validators(dic=True)
        for validator_slug in question.format_validators:
            format_validators[validator_slug]().validate(value, document)


class DocumentValidator:
    def validate(self, document, user, validation_context=None, **kwargs):
        if not validation_context:
            validation_context = self._validation_context(document)

        self._validate_required(validation_context)

        for answer in document.answers.filter(
            question_id__in=validation_context["visible_questions"]
        ):
            validator = AnswerValidator()
            validator.validate(
                document=document,
                question=answer.question,
                value=answer.value,
                documents=answer.documents.all(),
                user=user,
                validation_context=validation_context,
            )

    def _validation_context(self, document):
        # we need to build the context in two steps (for now), as
        # `self.visible_questions()` already needs a context to evaluate
        # `is_hidden` expressions
        intermediate_context = {
            "form": document.form,
            "document": document,
            "visible_questions": None,
            "jexl_cache": defaultdict(dict),
            "structure": structure.FieldSet(document, document.form),
        }

        intermediate_context["visible_questions"] = self.visible_questions(
            document, intermediate_context
        )
        return intermediate_context

    def visible_questions(self, document, validation_context=None):
        """Evaluate the visibility of the questions for the given context.

        This evaluates the `is_hidden` expression for each question to decide
        if the question is visible.
        Return a list of question slugs that are visible.
        """
        if not validation_context:
            validation_context = self._validation_context(document)
        visible_questions = []

        q_jexl = jexl.QuestionJexl(validation_context)
        for field in validation_context["structure"].children():
            question = field.question
            try:
                is_hidden = q_jexl.is_hidden(question)

                if is_hidden:
                    # no need to descend further
                    continue

                visible_questions.append(question.slug)
                if question.type == Question.TYPE_FORM:
                    # answers to questions in subforms are still in
                    # the top level document
                    sub_context = {**validation_context, "structure": field}
                    visible_questions.extend(
                        self.visible_questions(document, sub_context)
                    )

                elif question.type == Question.TYPE_TABLE:
                    row_visibles = set()
                    # make a copy of the validation context, so we
                    # can reuse it for each row
                    row_context = {**validation_context}
                    for row in field.children():
                        sub_context = {**row_context, "structure": row}
                        row_visibles.update(
                            self.visible_questions(document, sub_context)
                        )
                    visible_questions.extend(row_visibles)

            except (jexl.QuestionMissing, exceptions.ValidationError):
                raise
            except Exception as exc:
                log.error(
                    f"Error while evaluating `is_hidden` expression on question {question.slug}: "
                    f"{question.is_hidden}: {str(exc)}"
                )
                raise RuntimeError(
                    f"Error while evaluating `is_hidden` expression on question {question.slug}: "
                    f"{question.is_hidden}. The system log contains more information"
                )
        return visible_questions

    def _validate_required(self, validation_context):  # noqa: C901
        """Validate the 'requiredness' of the given answers.

        Raise exceptions if a required question is not answered.

        Since we're iterating and evaluating `is_hidden` as well for this
        purpose, we help our call site by returning a list of *non-hidden*
        question slugs.
        """
        required_but_empty = []

        q_jexl = jexl.QuestionJexl(validation_context)
        for field in validation_context["structure"].children():
            question = field.question
            try:
                is_hidden = question.slug not in validation_context["visible_questions"]
                if is_hidden:
                    continue

                # The above `is_hidden` is globally cached per question, mainly to optimize DB access.
                # This means a question could be marked "visible" as it would be visible
                # in another row, but would still be hidden in the local row, if this is a
                # table question context.  Thus, in this case we need to re-evaluate it's
                # hiddenness. Luckily, the JEXL evaluator caches those values (locally).
                with q_jexl.use_question_context(question.pk):
                    if q_jexl.is_hidden(question):
                        continue

                is_required = q_jexl.is_required(field)

                if question.type == Question.TYPE_FORM:
                    # form questions's answers are still in the top level document
                    sub_context = {**validation_context, "structure": field}
                    self._validate_required(sub_context)

                elif question.type == Question.TYPE_TABLE:
                    # We need to validate presence in at least one row, but only
                    # if the table question is required.
                    if is_required and not field.children():
                        raise CustomValidationError(
                            f"no rows in {question.slug}", slugs=[question.slug]
                        )
                    for row in field.children():
                        sub_context = {**validation_context, "structure": row}
                        self._validate_required(sub_context)
                else:
                    value = field.value()
                    if value in EMPTY_VALUES and is_required:
                        required_but_empty.append(question.slug)

            except CustomValidationError as exc:
                required_but_empty.extend(exc.slugs)

            except (jexl.QuestionMissing, exceptions.ValidationError):
                raise
            except Exception as exc:
                log.error(
                    f"Error while evaluating `is_required` expression on question {question.slug}: "
                    f"{question.is_required}: {str(exc)}"
                )

                raise RuntimeError(
                    f"Error while evaluating `is_required` expression on question {question.slug}: "
                    f"{question.is_required}. The system log contains more information"
                )

        if required_but_empty:
            raise CustomValidationError(
                f"Questions {','.join(required_but_empty)} are required but not provided.",
                slugs=required_but_empty,
            )


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


def get_document_validity(document, user):
    validator = DocumentValidator()
    is_valid = True
    errors = []

    try:
        validator.validate(document, user)
    except CustomValidationError as exc:
        is_valid = False
        detail = str(exc.detail[0])
        errors = [{"slug": slug, "error_msg": detail} for slug in exc.slugs]

    return {"id": document.id, "is_valid": is_valid, "errors": errors}
