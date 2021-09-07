import itertools

from django.db.models.signals import (
    m2m_changed,
    post_delete,
    post_init,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from caluma.caluma_core.events import filter_events
from caluma.utils import disable_raw

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
@filter_events(lambda instance: instance.default_answer is not None)
def cleanup_default_answer(sender, instance, **kwargs):
    """Ensure default_answers are cleanedup."""
    instance.default_answer.delete()


@receiver(post_init, sender=models.Document)
@filter_events(lambda instance: instance.family_id is None)
def set_document_family(sender, instance, **kwargs):
    """
    Ensure document has the family pointer set.

    This sets the document's family if not overruled or set already.
    The family will be in the corresponding mutations when a tree
    structure is created or restructured.
    """

    # can't use instance.set_family() here as the instance isn't
    # in DB yet, causing integrity errors
    instance.family = instance


def _update_calc_dependents(slug, old_expr, new_expr):
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


def _update_or_create_calc_answer(question, document):
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


# Update calc dependents on pre_save
#
# Every question that is referenced in a `calcExpression` will memoize the
# referencing calculated question. This list of calculation dependents is
# mutated whenever a calculated question is created, updated or deleted.


@receiver(pre_save, sender=models.Question)
@disable_raw
@filter_events(lambda instance: instance.type == models.Question.TYPE_CALCULATED_FLOAT)
def save_calc_dependents(sender, instance, **kwargs):

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
@filter_events(lambda instance: instance.type == models.Question.TYPE_CALCULATED_FLOAT)
def remove_calc_dependents(sender, instance, **kwargs):
    _update_calc_dependents(
        instance.slug, old_expr=instance.calc_expression, new_expr="false"
    )


# Update calculated answer on post_save
#
# Try to update the calculated answer value whenever a mutation on a possibly
# related model is performed.


@receiver(post_save, sender=models.Question)
@disable_raw
@filter_events(lambda instance: instance.type == models.Question.TYPE_CALCULATED_FLOAT)
def update_calc_from_question(sender, instance, created, update_fields, **kwargs):

    # TODO optimize: only update answers if calc_expression is updated
    # needs to happen during save() or __init__()

    for document in models.Document.objects.filter(form__questions=instance):
        _update_or_create_calc_answer(instance, document)


@receiver(post_save, sender=models.FormQuestion)
@disable_raw
@filter_events(
    lambda instance: instance.question.type == models.Question.TYPE_CALCULATED_FLOAT
)
def update_calc_from_form_question(sender, instance, created, **kwargs):
    for document in instance.form.documents.all():
        _update_or_create_calc_answer(instance.question, document)


@receiver(post_save, sender=models.Answer)
@disable_raw
@filter_events(lambda instance: instance.document and instance.question.calc_dependents)
def update_calc_from_answer(sender, instance, **kwargs):
    # If there is no document on the answer it means that it's a default
    # answer. They shouldn't trigger a recalculation of a calculated field
    # even when they are technically listed as a dependency.
    # Also skip non-referenced answers.

    for question in models.Question.objects.filter(
        pk__in=instance.question.calc_dependents
    ):
        _update_or_create_calc_answer(question, instance.document)


@receiver(post_save, sender=models.Document)
@disable_raw
@filter_events(lambda created: created)
def update_calc_from_document(sender, instance, created, **kwargs):

    for question in instance.form.questions.filter(
        type=models.Question.TYPE_CALCULATED_FLOAT
    ):
        _update_or_create_calc_answer(question, instance)


@receiver(m2m_changed, sender=models.AnswerDocument)
def update_calc_from_answerdocument(sender, instance, **kwargs):
    dependents = instance.document.form.questions.exclude(
        calc_dependents=[]
    ).values_list("calc_dependents", flat=True)

    dependent_questions = list(itertools.chain(*dependents))

    for question in models.Question.objects.filter(pk__in=dependent_questions):
        _update_or_create_calc_answer(question, instance.document)
