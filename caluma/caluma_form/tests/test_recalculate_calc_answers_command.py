import os

import pytest
from django.core.management import call_command

from caluma.caluma_form import structure
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


@pytest.mark.django_db
def test_recalculate_sibling_rows_in_table(form_factory, form_question_factory, caplog):

    root_form = form_factory(slug="root")
    row_form = form_factory(slug="row")

    table_q = form_question_factory(
        form=root_form,
        question__type=Question.TYPE_TABLE,
        question__slug="table",
        question__row_form=row_form,
    ).question

    column1 = form_question_factory(
        form=row_form,
        question__type=Question.TYPE_INTEGER,
        question__slug="col1",
        sort=2,
    ).question

    column2 = form_question_factory(
        form=row_form,
        question__slug="col2",
        question__type=Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression=f"'{column1}'|answer * 2",
        sort=1,
    ).question
    row_form.refresh_from_db()

    # Just to make sure ...
    column1.refresh_from_db()
    assert column1.calc_dependents == [column2.slug]

    main_doc = save_document(form=root_form)
    row0doc = save_document(form=row_form)
    row1doc = save_document(form=row_form)

    save_answer(question=table_q, document=main_doc, value=[row0doc.pk, row1doc.pk])
    row0doc.refresh_from_db()
    row1doc.refresh_from_db()
    assert row0doc.family == main_doc
    assert row1doc.family == main_doc

    save_answer(question=column1, value=10, document=row0doc)
    save_answer(question=column1, value=20, document=row1doc)

    main_doc.refresh_from_db()

    # Ensure (more for us devs) that we got the right structure
    assert structure.list_document_structure(main_doc) == [
        " FieldSet(root)",
        "    RowSet(table)",
        "       FieldSet(row)",
        "          Field(col1, 10)",
        "          Field(col2, 20)",
        "       FieldSet(row)",
        "          Field(col1, 20)",
        "          Field(col2, 40)",
    ]

    caplog.clear()
    with caplog.at_level("DEBUG"):
        save_answer(question=column1, value=99, document=row1doc)

    # col2 should only be updated once
    update_msgs = [msg for msg in caplog.messages if "updating question col2" in msg]
    assert len(update_msgs) == 1

    # Check for correct recalculation
    row0col2 = row0doc.answers.get(question=column2)
    row1col2 = row1doc.answers.get(question=column2)
    assert row0col2.value == 20  # 2*10
    assert row1col2.value == 198  # 99*2
