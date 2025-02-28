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

    row_doc1 = document_factory(form=sub_table.row_form, family=root_doc)
    answer_factory(document=row_doc1, question=row_field_1, date=datetime(2025, 1, 13))
    answer_factory(document=row_doc1, question=row_field_2, value=99.5)

    row_doc2 = document_factory(form=sub_table.row_form, family=root_doc)
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


def test_rowset_columns(simple_form_structure):
    fieldset = structure.FieldSet(simple_form_structure)

    table = fieldset.get_field("sub_table")

    expected_cols = [
        "row_field_1",
        "row_field_2",
        "row_calc",
    ]

    col_slugs = [q.slug for q in table.get_column_questions()]

    assert col_slugs == expected_cols


def test_options(simple_form_structure, form_question_factory, question_option_factory):
    choice_q = form_question_factory(
        question__type="choice", form=simple_form_structure.form
    ).question

    opts = question_option_factory.create_batch(4, question=choice_q)
    assert choice_q.options.exists()

    fieldset = structure.FieldSet(simple_form_structure)
    choice_field = fieldset.get_field(choice_q.slug)

    expected_opts = [qopt.option_id for qopt in opts]

    option_slugs = [opt.slug for opt in choice_field.get_options()]

    assert option_slugs == expected_opts


def test_dynamic_options(
    simple_form_structure, form_question_factory, dynamic_option_factory
):
    choice_q = form_question_factory(
        question__type="dynamic_choice", form=simple_form_structure.form
    ).question

    opts = dynamic_option_factory.create_batch(
        4, question=choice_q, document=simple_form_structure
    )
    assert choice_q.dynamicoption_set.exists()

    fieldset = structure.FieldSet(simple_form_structure)
    choice_field = fieldset.get_field(choice_q.slug)

    expected_opts = sorted([qopt.slug for qopt in opts])
    # We don't care about the ordering here, as internally the dyn options
    # are kept as a dict
    option_slugs = sorted(choice_field.get_dynamic_options().keys())

    assert option_slugs == expected_opts


def test_fastloader_deferred_form_load(simple_form_structure, form_factory, caplog):
    """Verify behaviour of the fastloader's form_by_id() method.

    FastLoader.form_by_id() needs to load any missing form if given an
    unknown form slug. This should not happen (things should be preloaded
    properly), so we also check for an appropriate warning message.
    """
    form = form_factory()

    loader = structure.FastLoader(simple_form_structure)
    expected_msg = f"Fastloader: Form {form.slug} was not preloaded - loading now"

    # Precondition, just to visualize the expected behaviour
    assert form.slug not in loader._forms

    # that form is not part of the structure - fastloader can
    # still be triggered to load it and it's structure though
    assert loader.form_by_id(form.slug) == form

    assert expected_msg in caplog.messages

    # Postcondition
    assert form.slug in loader._forms


def test_fastloader_question_for_answer(simple_form_structure):
    """Verify behaviour of the fastloader's question_for_answer() method."""
    fieldset = structure.FieldSet(simple_form_structure)

    loader = fieldset._fastloader

    field = fieldset.get_field("leaf1")

    question = loader.question_for_answer(field.answer)
    assert isinstance(question, Question)

    assert question.slug == field.slug()
