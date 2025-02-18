# Test cases for the (NEW!) structure utility class

from datetime import date, datetime

import pytest

from caluma.caluma_form import structure
from caluma.caluma_form.models import Answer, Question


@pytest.fixture()
def simple_form_structure(
    db, form_factory, form_question_factory, answer_factory, document_factory
):
    form = form_factory(slug="root")
    root_leaf1 = form_question_factory(
        form=form, question__type=Question.TYPE_TEXT, question__slug="leaf1", sort=90
    ).question
    root_leaf2 = form_question_factory(
        form=form,
        question__type=Question.TYPE_INTEGER,
        question__slug="leaf2",
        sort=80,
    ).question

    root_formquestion = form_question_factory(
        form=form, question__type=Question.TYPE_FORM, question__slug="subform", sort=70
    ).question
    assert root_formquestion.sub_form

    form_question_factory(
        form=root_formquestion.sub_form,
        question__type=Question.TYPE_TEXT,
        question__slug="sub_leaf1",
        sort=60,
    )
    form_question_factory(
        form=root_formquestion.sub_form,
        question__type=Question.TYPE_INTEGER,
        question__slug="sub_leaf2",
        sort=50,
    )

    sub_table = form_question_factory(
        form=root_formquestion.sub_form,
        question__type=Question.TYPE_TABLE,
        question__slug="sub_table",
        sort=40,
    ).question

    row_field_1 = form_question_factory(
        form=sub_table.row_form,
        question__type=Question.TYPE_DATE,
        question__slug="row_field_1",
        sort=30,
    ).question
    row_field_2 = form_question_factory(
        form=sub_table.row_form,
        question__type=Question.TYPE_FLOAT,
        question__slug="row_field_2",
        sort=20,
    ).question

    # row field has a dependency *outside* the row, and one *inside*
    form_question_factory(
        form=sub_table.row_form,
        question__type=Question.TYPE_CALCULATED_FLOAT,
        question__calc_expression=f"'{root_leaf2.slug}'|answer + '{row_field_2.slug}'|answer",
        question__slug="row_calc",
        sort=10,
    )

    root_doc = document_factory(form=form)

    answer_factory(document=root_doc, question=root_leaf1, value="Some Value")
    answer_factory(document=root_doc, question=root_leaf2, value=33)
    table_ans = answer_factory(document=root_doc, question=sub_table)

    row_doc1 = document_factory(form=sub_table.row_form)
    answer_factory(document=row_doc1, question=row_field_1, date=datetime(2025, 1, 13))
    answer_factory(document=row_doc1, question=row_field_2, value=99.5)

    row_doc2 = document_factory(form=sub_table.row_form)
    answer_factory(document=row_doc2, question=row_field_1, date=datetime(2025, 1, 10))
    answer_factory(document=row_doc2, question=row_field_2, value=23.0)

    table_ans.documents.add(row_doc1)
    table_ans.documents.add(row_doc2)

    return root_doc


def test_printing_structure(simple_form_structure):
    out_lines = []

    def fake_print(*args):
        out_lines.append(" ".join([str(x) for x in args]))

    fieldset = structure.FieldSet(simple_form_structure)
    structure.print_structure(fieldset, print_fn=fake_print)

    assert out_lines == [
        " FieldSet(root)",
        "    Field(leaf1, Some Value)",
        "    Field(leaf2, 33)",
        "    FieldSet(measure-evening)",
        "       Field(sub_leaf1, None)",
        "       Field(sub_leaf2, None)",
        "       RowSet(too-wonder-option)",
        "          FieldSet(too-wonder-option)",
        "             Field(row_field_1, 2025-01-13)",
        "             Field(row_field_2, 99.5)",
        "             Field(row_calc, None)",
        "          FieldSet(too-wonder-option)",
        "             Field(row_field_1, 2025-01-10)",
        "             Field(row_field_2, 23.0)",
        "             Field(row_calc, None)",
    ]


@pytest.mark.parametrize("empty", [True, False])
def test_root_getvalue(simple_form_structure, empty):
    if empty:
        Answer.objects.all().delete()

    fieldset = structure.FieldSet(simple_form_structure)

    expected_value = (
        {}
        if empty
        else {
            "leaf1": "Some Value",
            "leaf2": 33,
            "subform": {
                "sub_leaf1": None,
                "sub_leaf2": None,
                "sub_table": [
                    {
                        "row_calc": None,
                        "row_field_1": date(2025, 1, 13),
                        "row_field_2": 99.5,
                    },
                    {
                        "row_calc": None,
                        "row_field_1": date(2025, 1, 10),
                        "row_field_2": 23.0,
                    },
                ],
            },
        }
    )
    assert fieldset.get_value() == expected_value


@pytest.mark.parametrize("hidden", ["true", "false"])
def test_hidden_fieldset(simple_form_structure, hidden):
    # We hide the subform to test it's get_value() result
    subform_q = Question.objects.get(slug="subform")
    subform_q.is_hidden = hidden
    subform_q.save()

    fieldset = structure.FieldSet(simple_form_structure)

    expected_value = (
        {
            "leaf1": "Some Value",
            "leaf2": 33,
            "subform": {},
        }
        if (hidden == "true")
        else {
            "leaf1": "Some Value",
            "leaf2": 33,
            "subform": {
                "sub_leaf1": None,
                "sub_leaf2": None,
                "sub_table": [
                    {
                        "row_calc": None,
                        "row_field_1": date(2025, 1, 13),
                        "row_field_2": 99.5,
                    },
                    {
                        "row_calc": None,
                        "row_field_1": date(2025, 1, 10),
                        "row_field_2": 23.0,
                    },
                ],
            },
        }
    )
    assert fieldset.get_value() == expected_value


def test_find_missing_answer(simple_form_structure, answer_factory):
    fieldset = structure.FieldSet(simple_form_structure)

    # Find unrelated answer - should not be found
    assert fieldset.find_field_by_answer(answer_factory()) is None


def test_hidden_root_field(simple_form_structure):
    fieldset = structure.FieldSet(simple_form_structure)

    # Can never fail: Root field must always be visible (as it doesn't have
    # a question associated... ¯\_(ツ)_/¯)
    assert not fieldset.is_hidden()


def test_empty_formfield(simple_form_structure):
    """Verify form fields to be empty if none of their sub fields have answers.

    If a form question (subform) has no answer within, we consider it empty
    and `is_empty()` should return `True`.
    """
    fieldset = structure.FieldSet(simple_form_structure)

    subform = fieldset.get_field("subform")
    for field in subform.get_all_fields():
        if field.answer:
            field.answer.delete()

    # new fieldset to avoid caching leftovers
    fieldset = structure.FieldSet(simple_form_structure)
    subform = fieldset.get_field("subform")

    assert subform.is_empty()


def test_hidden_formfield(simple_form_structure):
    """A hidden fieldset (form field) should be considered empty when hidden.

    As hidden questions are not shown, their value should also not be considered
    during evaluation. Therefore, `is_empty()` should return True if the
    corresponding question is hidden.
    """
    fieldset = structure.FieldSet(simple_form_structure)

    subform = fieldset.get_field("subform")
    subform.question.is_hidden = "true"
    subform.question.save()

    # The form is not really empty, but it's hidden, so is_empty() should
    # return True nonetheless
    assert subform.is_empty()
