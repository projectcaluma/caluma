import itertools

from django.db.models.signals import (
    post_delete,
    post_init,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from caluma.utils import update_model

from . import models, structure
from .jexl import QuestionJexl


@receiver(pre_create_historical_record, sender=models.HistoricalAnswer)
def set_historical_answer_type(sender, **kwargs):
    """Receiver for historical answer pre_save signal setting question type."""
    historical_answer = kwargs["history_instance"]

    try:
        # can take the current question, assuming the question type is not changed in a datarace
        historical_answer.history_question_type = historical_answer.question.type
    except models.Question.DoesNotExist:
        # This happens when deleting a question with a default_answer. As the Answer
        # has to exist for this to happen, we can safely assume to already have a
        # historical record of it. So we're taking the question type from the previous
        # revision.
        previous = historical_answer.get_previous_by_history_date()
        historical_answer.history_question_type = previous.history_question_type


@receiver(post_delete, sender=models.Question)
def cleanup_default_answer(sender, instance, **kwargs):
    """Ensure default_answers are cleanedup."""
    if instance.default_answer is not None:
        instance.default_answer.delete()


@receiver(post_init, sender=models.Document)
def set_document_family(sender, instance, **kwargs):
    """
    Ensure document has the family pointer set.

    This sets the document's family if not overruled or set already.
    The family will be in the corresponding mutations when a tree
    structure is created or restructured.
    """
    if instance.family_id is None:
        # can't use instance.set_family() here as the instance isn't
        # in DB yet, causing integrity errors
        instance.family = instance


def _update_calc_dependents(slug, old_expr, new_expr):
    jexl = QuestionJexl()
    old_q = set(jexl.extract_referenced_questions(old_expr))
    new_q = set(jexl.extract_referenced_questions(new_expr))

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


def _update_or_create_calc_answer(question, document):
    root_doc = document.family
    root_form = document.family.form

    struc = structure.FieldSet(root_doc, root_form)

    for path in struc.paths_to_question(question.slug):
        element = struc
        for formquestion in path:
            element = element.get_field(formquestion.slug)

        jexl = QuestionJexl(
            {
                "form": element.form,
                "document": element.document,
                "structure": element.parent(),
            }
        )
        value = jexl.evaluate_calc_value(element)

        try:
            ans = models.Answer.objects.get(
                question=question, document=element.document
            )
            update_model(ans, {"value": value})
        except models.Answer.DoesNotExist:
            models.Answer.objects.create(
                question=question, document=element.document, value=value
            )


@receiver(pre_save, sender=models.Question)
def save_calc_dependents(sender, instance, **kwargs):
    if instance.type != models.Question.TYPE_CALCULATED_FLOAT:
        return

    original = models.Question.objects.filter(pk=instance.pk).first()
    if not original:
        _update_calc_dependents(
            instance.slug, old_expr="false", new_expr=instance.calc_expression
        )

    elif original.calc_expression != instance.calc_expression:
        _update_calc_dependents(
            instance.slug,
            old_expr=original.calc_expression,
            new_expr=instance.calc_expression,
        )


@receiver(pre_delete, sender=models.Question)
def remove_calc_dependents(sender, instance, **kwargs):
    if instance.type != models.Question.TYPE_CALCULATED_FLOAT:
        return

    _update_calc_dependents(
        instance.slug, old_expr=instance.calc_expression, new_expr="false"
    )


@receiver(post_save, sender=models.Question)
def update_calc_from_question(sender, instance, created, update_fields, **kwargs):
    if (
        instance.type != models.Question.TYPE_CALCULATED_FLOAT
        or not created
        and not (update_fields and "calc_expression" in update_fields)
    ):
        return

    for document in models.Document.objects.filter(form__questions=instance):
        _update_or_create_calc_answer(instance, document)


@receiver(post_save, sender=models.FormQuestion)
def update_calc_from_form_question(sender, instance, created, **kwargs):
    if instance.question.type != models.Question.TYPE_CALCULATED_FLOAT:
        return

    for document in instance.form.documents.all():
        _update_or_create_calc_answer(instance.question, document)


@receiver(post_save, sender=models.Answer)
def update_calc_from_answer(sender, instance, **kwargs):
    for question in models.Question.objects.filter(
        pk__in=instance.question.calc_dependents or []
    ):
        _update_or_create_calc_answer(question, instance.document)


@receiver(post_save, sender=models.Document)
def update_calc_from_document(sender, instance, created, **kwargs):
    if not created:
        return

    for question in instance.form.questions.filter(
        type=models.Question.TYPE_CALCULATED_FLOAT
    ):
        _update_or_create_calc_answer(question, instance)


@receiver(post_delete, sender=models.AnswerDocument)
@receiver(post_save, sender=models.AnswerDocument)
def update_calc_from_answerdocument(sender, instance, **kwargs):
    dependents = instance.document.form.questions.exclude(
        calc_dependents=[]
    ).values_list("calc_dependents", flat=True)

    dependent_questions = itertools.chain(*dependents)

    for question in models.Question.objects.filter(pk__in=dependent_questions):
        _update_or_create_calc_answer(question, instance.document)
