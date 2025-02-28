from django.db.models.signals import (
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

from . import models
from .utils import update_calc_dependents, update_or_create_calc_answer


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
        update_calc_dependents(
            instance.slug, old_expr="false", new_expr=instance.calc_expression
        )
        instance.calc_expression_changed = True

    elif original.calc_expression != instance.calc_expression:
        update_calc_dependents(
            instance.slug,
            old_expr=original.calc_expression,
            new_expr=instance.calc_expression,
        )
        instance.calc_expression_changed = True
    else:
        instance.calc_expression_changed = False


@receiver(pre_delete, sender=models.Question)
@filter_events(lambda instance: instance.type == models.Question.TYPE_CALCULATED_FLOAT)
def remove_calc_dependents(sender, instance, **kwargs):
    update_calc_dependents(
        instance.slug, old_expr=instance.calc_expression, new_expr="false"
    )


# Update calculated answer on post_save
#
# Try to update the calculated answer value whenever a mutation on a possibly
# related model is performed.


@receiver(post_save, sender=models.Question)
@disable_raw
@filter_events(lambda instance: instance.type == models.Question.TYPE_CALCULATED_FLOAT)
@filter_events(lambda instance: getattr(instance, "calc_expression_changed", False))
def update_calc_from_question(sender, instance, created, update_fields, **kwargs):
    # TODO: we need to find documents that contain this form as a subform
    # as well. This would only find documents where the question is attached
    # top-level.
    for document in models.Document.objects.filter(form__questions=instance).iterator():
        update_or_create_calc_answer(instance, document)


@receiver(post_save, sender=models.FormQuestion)
@disable_raw
@filter_events(
    lambda instance: instance.question.type == models.Question.TYPE_CALCULATED_FLOAT
)
def update_calc_from_form_question(sender, instance, created, **kwargs):
    # TODO: we need to find documents that contain this form as a subform
    # as well. This would only find documents where the question is attached
    # top-level.
    for document in instance.form.documents.all().iterator():
        update_or_create_calc_answer(instance.question, document)
