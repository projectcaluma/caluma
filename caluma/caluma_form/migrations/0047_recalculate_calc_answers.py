from django.db import migrations

from caluma.caluma_form.jexl import QuestionJexl
from caluma.caluma_form.structure import FieldSet


def recalculate_answer(answer):
    """
    Recalculate a single calc-answer.

    This is more or less a copy/paste from `_update_or_create_calc_answer` in order to
    use the old models.
    """
    root_doc = answer.document.family

    struc = FieldSet(root_doc, root_doc.form)
    field = struc.get_field(answer.question.slug)

    # skip if question doesn't exist in this document structure
    if field is None:  # pragma: no cover
        return

    jexl = QuestionJexl(
        {"form": field.form, "document": field.document, "structure": field.parent()}
    )

    # Ignore errors because we might evaluate partially built forms. So we might be
    # missing some answers or the expression might be invalid, in which case we return
    # None
    value = jexl.evaluate(field.question.calc_expression, raise_on_error=False)

    answer.value = value
    answer.save()


def recalculate_all_answers(apps, _):
    AnswerModel = apps.get_model("caluma_form.Answer")

    calc_answers = AnswerModel.objects.filter(
        question__type="calculated_float", document__isnull=False
    )
    for answer in calc_answers.iterator():
        recalculate_answer(answer)


class Migration(migrations.Migration):

    dependencies = [
        ("caluma_form", "0046_file_answer_reverse_keys"),
    ]

    operations = [
        migrations.RunPython(recalculate_all_answers, migrations.RunPython.noop),
    ]
