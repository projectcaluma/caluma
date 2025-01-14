# Test cases for the (NEW!) structure utility class
from functools import singledispatch
from pathlib import Path

import pytest
from django.core.management import call_command

from caluma.caluma_form import api, structure
from caluma.caluma_form.models import AnswerDocument, Document, Form, Question


def get_doc_structure(document):
    """Return a list of strings that represent the given document's structure."""

    ind = {"i": 0}
    res = []

    @singledispatch
    def visit(vis):
        raise Exception(f"generic visit(): {vis}")

    @visit.register(structure.FieldSet)
    def _(vis):
        res.append("   " * ind["i"] + f"FieldSet({vis.form.slug})")
        ind["i"] += 1
        for c in vis.children():
            visit(c)
        ind["i"] -= 1

    @visit.register(structure.Element)
    def _(vis):
        res.append(
            "   " * ind["i"]
            + f"Field({vis.question.slug}, {vis.answer.value if vis.answer else None})"
        )
        ind["i"] += 1
        for c in vis.children():
            visit(c)
        ind["i"] -= 1

    struc = structure.FieldSet(document, document.form)
    visit(struc)
    return res


@pytest.fixture
def complex_jexl_form():
    # Complex JEXL evaluation tests:
    # * Recalculation witin table rows
    # * Visibility checks in "outer" form with indirect calc question evaluation
    data_file = Path(__file__).parent / "test_data/complex_jexl_context.json"
    assert data_file.exists()
    call_command("loaddata", str(data_file))
    return Form.objects.get(slug="demo-formular-1")


@pytest.fixture
def complex_jexl_doc(complex_jexl_form):
    # -> root_doc, row1, row2 as tuple
    doc = Document.objects.create(form=complex_jexl_form)

    api.save_answer(
        Question.objects.get(pk="demo-outer-question-1"),
        doc,
        value="demo-outer-question-1-outer-option-a",
    )
    table_ans = api.save_answer(
        Question.objects.get(pk="demo-outer-table-question-1"),
        doc,
    )

    row1 = AnswerDocument.objects.create(
        answer=table_ans,
        document=Document.objects.create(form=table_ans.question.row_form, family=doc),
        sort=2,
    ).document
    row2 = AnswerDocument.objects.create(
        answer=table_ans,
        document=Document.objects.create(form=table_ans.question.row_form, family=doc),
        sort=1,
    ).document

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row1, value=3
    )

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row2, value=20
    )
    return doc, row1, row2


def test_evaluating_calc_inside_table(
    transactional_db, complex_jexl_form, complex_jexl_doc
):
    doc, *_ = complex_jexl_doc

    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 3)",
        "         Field(demo-table-question-2, 1)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 20)",
        "         Field(demo-table-question-2, 100)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]


def test_update_calc_dependency_inside_table(
    transactional_db, complex_jexl_form, complex_jexl_doc
):
    doc, row1, row2 = complex_jexl_doc

    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 3)",
        "         Field(demo-table-question-2, 1)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 2)",
        "         Field(demo-table-question-2, 1)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row1, value=30
    )
    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 30)",
        "         Field(demo-table-question-2, 100)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 2)",
        "         Field(demo-table-question-2, 1)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row1, value=3
    )
    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 3)",
        "         Field(demo-table-question-2, 1)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 2)",
        "         Field(demo-table-question-2, 1)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row2, value=20
    )
    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 3)",
        "         Field(demo-table-question-2, 1)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 20)",
        "         Field(demo-table-question-2, 100)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row2, value=2
    )
    assert get_doc_structure(doc) == [
        "FieldSet(demo-formular-1)",
        "   Field(demo-outer-table-question-1, None)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 3)",
        "         Field(demo-table-question-2, 1)",
        "      FieldSet(demo-table-form-1)",
        "         Field(demo-table-question-1, 2)",
        "         Field(demo-table-question-2, 1)",
        "   Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "   Field(demo-outer-table-question-2, None)",
    ]
