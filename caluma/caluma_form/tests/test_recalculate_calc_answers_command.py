import os

from django.core.management import call_command

from caluma.caluma_form.api import save_answer, save_document
from caluma.caluma_form.models import Question


def test_recalculate_calc_answers(
    db,
    form_factory,
    question_factory,
    form_question_factory,
):
    # set up form structure
    main_form_question = form_question_factory(
        question__type=Question.TYPE_INTEGER, question__slug="dep1_main"
    )
    main_form = main_form_question.form
    dep1_main = main_form_question.question

    row_form = form_factory(slug="row_form")
    table_question = question_factory(
        type="table",
        slug="table_question",
        row_form=row_form,
        is_required="true",
        is_hidden="false",
    )
    form_question_factory(form=main_form, question=table_question)

    row_form_question = form_question_factory(
        form=row_form,
        question__type=Question.TYPE_INTEGER,
        question__slug="dep2_row",
        question__is_required=True,
    )
    dep2_row = row_form_question.question

    form_question_factory(
        form=main_form,
        question__slug="calc_question",
        question__type=Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression=(
            f'"dep1_main"|answer(0) + "{table_question.slug}"|answer([])|mapby("dep2_row")|sum'
        ),
    )

    # assert calc_dependents
    dep1_main.refresh_from_db()
    dep2_row.refresh_from_db()
    assert dep1_main.calc_dependents == ["calc_question"]
    assert dep2_row.calc_dependents == ["calc_question"]

    # set up document and answers
    main_doc = save_document(form=main_form)
    save_answer(question=dep1_main, value=10, document=main_doc)
    row_doc = save_document(form=row_form)
    save_answer(question=dep2_row, value=13, document=row_doc)
    # make sure table questions' calc dependents are up to date
    table_question.refresh_from_db()
    save_answer(table_question, document=main_doc, value=[str(row_doc.pk)])
    calc_answer = main_doc.answers.get(question_id="calc_question")

    # assert calc bug is fixed
    assert calc_answer.value == 23

    # set calc_answer.value to 10, like it would have been without the fix
    calc_answer.value = 10
    calc_answer.save()

    call_command("recalculate_calc_answers", stderr=open(os.devnull, "w"))

    # assert correct calc_value after migration
    calc_answer.refresh_from_db()
    assert calc_answer.value == 23
