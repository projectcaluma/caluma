import pytest

from caluma.caluma_form import calc_questions, models, structure
from caluma.caluma_form.api import save_answer


@pytest.mark.django_db
def test_recalculate_and_update_dependents(
    form_factory, form_question_factory, document_factory, answer_factory
):
    """Test recalculate_and_update_dependents utility."""
    form = form_factory(slug="calc_test")

    q_a = form_question_factory(
        form=form, question__type=models.Question.TYPE_INTEGER, question__slug="q_a"
    ).question

    q_b = form_question_factory(
        form=form,
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__slug="q_b",
        question__calc_expression=f"'{q_a.slug}'|answer * 2",
    ).question

    q_c = form_question_factory(
        form=form,
        question__type=models.Question.TYPE_CALCULATED_FLOAT,
        question__slug="q_c",
        question__calc_expression=f"'{q_b.slug}'|answer * 2",
    ).question

    # Refresh to ensure calc_dependents are set
    q_a.refresh_from_db()
    q_b.refresh_from_db()
    assert q_b.slug in q_a.calc_dependents
    assert q_c.slug in q_b.calc_dependents

    doc = document_factory(form=form)
    save_answer(question=q_a, document=doc, value=10)

    root = structure.FieldSet(doc)
    field_a = root.get_field(q_a.slug)
    field_b = root.get_field(q_b.slug)
    field_c = root.get_field(q_c.slug)

    # Refresh A in the structure to ensure B and C are also refreshed
    field_a.refresh()

    # Force recalculation of B and its dependents (C)
    calc_questions.recalculate_and_update_dependents(field_b)

    assert field_b.get_value() == 20.0
    assert field_c.get_value() == 40.0

    # Change A and verify that only calling it on B updates B and C
    save_answer(question=q_a, document=doc, value=5)
    # Ensure field_a in our structure sees the new value
    field_a.refresh()

    # save_answer already triggered B and C updates via signals.
    # To test that recalculate_and_update_dependents(field_b) actually
    # triggers C when B changes, we manually set B and C to wrong values first.
    models.Answer.objects.filter(question=q_b, document=doc).update(value=0)
    models.Answer.objects.filter(question=q_c, document=doc).update(value=0)
    field_b.refresh()
    field_c.refresh()
    assert field_b.get_value() == 0
    assert field_c.get_value() == 0

    calc_questions.recalculate_and_update_dependents(field_b)

    assert field_b.get_value() == 10.0
    assert field_c.get_value() == 20.0


@pytest.mark.django_db
def test_new_table_row_recalculation(
    form_factory, question_factory, form_question_factory, document_factory
):
    """Test that calculated fields in new table rows are recalculated."""
    # Setup form
    form = form_factory(slug="form")
    q_root = question_factory(slug="q_root", type=models.Question.TYPE_INTEGER)
    form_question_factory(form=form, question=q_root)

    row_form = form_factory(slug="row_form")
    q_table = question_factory(
        slug="q_table", type=models.Question.TYPE_TABLE, row_form=row_form
    )
    form_question_factory(form=form, question=q_table)

    q_calc = question_factory(
        slug="q_calc",
        type=models.Question.TYPE_CALCULATED_FLOAT,
        calc_expression="'q_root'|answer * 2",
    )
    form_question_factory(form=row_form, question=q_calc)

    # Create document and set q_root
    doc = document_factory(form=form)
    save_answer(question=q_root, document=doc, value=21)

    # Add first row to table
    row1 = document_factory(form=row_form)
    save_answer(question=q_table, document=doc, value=[str(row1.pk)])

    # Verify row1 calc
    ans1 = models.Answer.objects.get(question=q_calc, document=row1)
    assert ans1.value == 42.0

    # Add second row to table, DON'T change q_root
    row2 = document_factory(form=row_form)

    # This calls SaveAnswerLogic.update for the table answer
    save_answer(question=q_table, document=doc, value=[str(row1.pk), str(row2.pk)])

    # Verify row2 calc
    ans2 = models.Answer.objects.get(question=q_calc, document=row2)
    assert ans2.value == 42.0
