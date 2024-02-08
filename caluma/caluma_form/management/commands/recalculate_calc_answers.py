from django.core.management.base import BaseCommand

from caluma.caluma_form.models import Answer, Question
from caluma.caluma_form.utils import update_or_create_calc_answer


class Command(BaseCommand):
    """
    Recalculate calculated answers containing values from TableAnswers.

    Due to a bug, answers to calculated questions were wrong, if they contained values
    from table rows. This command recalculates all of them.
    """

    help = "Recalculate calculated answers containing values from TableAnswers."

    def handle(self, *args, **options):
        affected_questions = (
            Question.objects.filter(type="table")
            .exclude(calc_dependents=[])
            .values_list("calc_dependents", flat=True)
        )

        affected_questions_clean = set(
            [slug for entry in affected_questions for slug in entry]
        )

        calc_answers = Answer.objects.filter(
            question__type="calculated_float",
            document__isnull=False,
            question__slug__in=affected_questions_clean,
        )

        for answer in calc_answers.iterator():
            update_or_create_calc_answer(answer.question, answer.document)
