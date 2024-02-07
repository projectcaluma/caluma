from typing import Any, Optional

from caluma.caluma_form import domain_logic, models, structure
from caluma.caluma_form.jexl import QuestionJexl
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
    answer = domain_logic.SaveAnswerLogic.get_new_answer(data, user, answer)

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


def update_calc_dependents(slug, old_expr, new_expr):
    jexl = QuestionJexl()
    old_q = set(
        list(jexl.extract_referenced_questions(old_expr))
        + list(jexl.extract_referenced_mapby_questions(old_expr))
    )
    new_q = set(
        list(jexl.extract_referenced_questions(new_expr))
        + list(jexl.extract_referenced_mapby_questions(new_expr))
    )

    to_add = new_q - old_q
    to_remove = old_q - new_q

    questions = models.Question.objects.filter(pk__in=list(to_add | to_remove))

    for question in questions:
        deps = set(question.calc_dependents)
        if question.slug in to_add:
            deps.add(slug)
        else:
            deps.remove(slug)
        question.calc_dependents = list(deps)
        question.save()


def update_or_create_calc_answer(question, document):
    root_doc = document.family

    struc = structure.FieldSet(root_doc, root_doc.form)
    field = struc.get_field(question.slug)

    # skip if question doesn't exist in this document structure
    if field is None:
        return

    jexl = QuestionJexl(
        {"form": field.form, "document": field.document, "structure": field.parent()}
    )

    # Ignore errors because we evaluate greedily as soon as possible. At
    # this moment we might be missing some answers or the expression might
    # be invalid, in which case we return None
    value = jexl.evaluate(field.question.calc_expression, raise_on_error=False)

    models.Answer.objects.update_or_create(
        question=question, document=field.document, defaults={"value": value}
    )


def recalculate_answers_from_document(instance):
    if (instance.family or instance).meta.get("_defer_calculation"):
        return
    for question in models.Form.get_all_questions(
        [(instance.family or instance).form_id]
    ).filter(type=models.Question.TYPE_CALCULATED_FLOAT):
        update_or_create_calc_answer(question, instance)
