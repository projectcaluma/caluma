from typing import Any, Optional

from caluma.caluma_form import domain_logic, models
from caluma.caluma_user.models import BaseUser


def save_answer(
    question: models.Question,
    document: Optional[models.Document] = None,
    user: Optional[BaseUser] = None,
    value: Optional[Any] = None,
    context: Optional[dict] = None,
    **kwargs
) -> models.Answer:
    """
    Save an answer for given question, document.

    Similar to saveDocumentStringAnswer and the likes, it performes upsert.
    :param value: Must match the question type
    """

    data = {"question": question, "document": document, "value": value}
    data.update(kwargs)

    answer = models.Answer.objects.filter(question=question, document=document).first()
    answer = domain_logic.SaveAnswerLogic.get_new_answer(data, user, answer)

    return answer


def save_default_answer(
    question: models.Question,
    user: Optional[BaseUser] = None,
    value: Optional[Any] = None,
    **kwargs
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
