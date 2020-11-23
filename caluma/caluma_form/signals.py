from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from . import models


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
