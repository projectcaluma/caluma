from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from . import models


@receiver(pre_create_historical_record, sender=models.HistoricalAnswer)
def set_historical_answer_type(sender, **kwargs):
    """Receiver for historical answer pre_save signal setting question type."""
    historical_answer = kwargs["history_instance"]

    # can take the current question, assuming the question type is not changed in a datarace
    historical_answer.history_question_type = historical_answer.question.type
