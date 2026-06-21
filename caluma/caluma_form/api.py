from collections.abc import Iterable
from typing import Any, Optional

from caluma.caluma_form import domain_logic, models, validators
from caluma.caluma_user.models import BaseUser


def save_answer(
    question: models.Question,
    document: Optional[models.Document] = None,
    user: Optional[BaseUser] = None,
    value: Optional[Any] = None,
    context: Optional[dict] = None,
    **kwargs,
) -> models.Answer:
    """
    Save an answer for given question, document.

    Similar to saveDocumentStringAnswer and the likes, it performes upsert.
    :param value: Must match the question type
    """

    data = {"question": question, "document": document, "value": value}
    data.update(kwargs)

    answer = models.Answer.objects.filter(question=question, document=document).first()
    answer = domain_logic.SaveAnswerLogic.get_new_answer(
        data, user, answer, context=context
    )

    return answer


def save_default_answer(
    question: models.Question,
    user: Optional[BaseUser] = None,
    value: Optional[Any] = None,
    **kwargs,
) -> models.Answer:
    """
    Save default_answer for given question.

    Similar to saveDefaultStringAnswer and the likes, it performes upsert.
    :param value: Must match the question type
    """

    data = {"question": question, "value": value}
    data.update(kwargs)

    answer = question.default_answer
    answer = domain_logic.SaveDefaultAnswerLogic.get_new_answer(data, user, answer)

    return answer


def save_document(
    form: models.Form,
    meta: Optional[dict] = None,
    document: Optional[models.Document] = None,
    user: Optional[BaseUser] = None,
) -> models.Document:
    """Save a document for a given form."""

    if meta is None:
        meta = {}

    if not document:
        return domain_logic.SaveDocumentLogic.create(
            {"form": form, "meta": meta}, user=user
        )

    domain_logic.SaveDocumentLogic.update(
        document, {"form": form, "meta": meta}, user=user
    )
    return document


def copy_form(
    source: models.Form,
    slug: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_published: Optional[bool] = None,
    user: Optional[BaseUser] = None,
) -> models.Form:
    """Copy a form."""

    return domain_logic.CopyFormLogic.copy(
        {
            "source": source,
            "slug": slug,
            "name": name,
            "description": description,
            "is_published": False if is_published is None else is_published,
        },
        user=user,
    )


def save_form(
    slug: str,
    name: Any,
    description: Any = "",
    meta: Optional[dict] = None,
    is_published: bool = False,
    is_archived: bool = False,
    form: Optional[models.Form] = None,
    user: Optional[BaseUser] = None,
) -> models.Form:
    """Save (create or update) a form."""

    data = {
        "slug": slug,
        "name": name,
        "description": description,
        "meta": {} if meta is None else meta,
        "is_published": is_published,
        "is_archived": is_archived,
    }

    if not form:
        return domain_logic.BaseLogic.create(models.Form, data, user=user)

    domain_logic.BaseLogic.update(form, data, user=user)
    return form


def save_question(
    slug: str,
    label: Any,
    type: str,
    is_required: str = "false",
    is_hidden: str = "false",
    placeholder: Any = None,
    hint_text: Any = None,
    info_text: Any = None,
    meta: Optional[dict] = None,
    configuration: Optional[dict] = None,
    row_form: Optional[models.Form] = None,
    sub_form: Optional[models.Form] = None,
    question: Optional[models.Question] = None,
    user: Optional[BaseUser] = None,
) -> models.Question:
    """Save (create or update) a question."""

    data = {
        "slug": slug,
        "label": label,
        "type": type,
        "is_required": is_required,
        "is_hidden": is_hidden,
        "meta": {} if meta is None else meta,
        "configuration": {} if configuration is None else configuration,
        "row_form": row_form,
        "sub_form": sub_form,
    }

    for key, value in (
        ("placeholder", placeholder),
        ("hint_text", hint_text),
        ("info_text", info_text),
    ):
        if value is not None:
            data[key] = value

    validators.QuestionValidator().validate(data)

    if not question:
        return domain_logic.BaseLogic.create(models.Question, data, user=user)

    domain_logic.BaseLogic.update(question, data, user=user)
    return question


def save_option(
    slug: str,
    label: Any,
    is_hidden: str = "false",
    meta: Optional[dict] = None,
    is_archived: bool = False,
    option: Optional[models.Option] = None,
    user: Optional[BaseUser] = None,
) -> models.Option:
    """Save (create or update) an option."""

    data = {
        "slug": slug,
        "label": label,
        "is_hidden": is_hidden,
        "meta": {} if meta is None else meta,
        "is_archived": is_archived,
    }

    if not option:
        return domain_logic.BaseLogic.create(models.Option, data, user=user)

    domain_logic.BaseLogic.update(option, data, user=user)
    return option


def save_form_questions(
    form: models.Form,
    questions: Iterable[models.Question],
    user: Optional[BaseUser] = None,
) -> list[models.FormQuestion]:
    """Synchronize form questions preserving input order."""

    models.FormQuestion.objects.filter(form=form).delete()
    form_questions = [
        models.FormQuestion(
            form=form,
            question=question,
            sort=sort,
            created_by_user=user.username if user else None,
            created_by_group=user.group if user else None,
            modified_by_user=user.username if user else None,
            modified_by_group=user.group if user else None,
        )
        for sort, question in enumerate(reversed(list(questions)), start=1)
    ]
    for form_question in form_questions:
        form_question.save()
    return form_questions


def save_question_options(
    question: models.Question,
    options: Iterable[models.Option],
    user: Optional[BaseUser] = None,
) -> list[models.QuestionOption]:
    """Synchronize question options preserving input order."""

    models.QuestionOption.objects.filter(question=question).delete()
    question_options = [
        models.QuestionOption(
            question=question,
            option=option,
            sort=sort,
            created_by_user=user.username if user else None,
            created_by_group=user.group if user else None,
            modified_by_user=user.username if user else None,
            modified_by_group=user.group if user else None,
        )
        for sort, option in enumerate(reversed(list(options)), start=1)
    ]
    for question_option in question_options:
        question_option.save()
    return question_options
