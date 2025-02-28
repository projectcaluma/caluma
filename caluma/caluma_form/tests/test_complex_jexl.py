# Test cases for the (NEW!) structure utility class
from pathlib import Path

import pytest
from django.core.management import call_command

from caluma.caluma_form import api, structure
from caluma.caluma_form.models import AnswerDocument, Document, Form, Question


@pytest.fixture
def complex_jexl_form():
    """Return a form with a bit of structure.

    The structure is as follows:

        demo-formular-1 (Root form)
           demo-outer-table-question-1 (Table)
              demo-table-form-1 (Row form)
                 demo-table-question-1 (Integer)
                 demo-table-question-2 (Calculated)
           demo-outer-question-1
           demo-outer-table-question-2
    """
    # Complex JEXL evaluation tests:
    # * Recalculation witin table rows
    # * Visibility checks in "outer" form with indirect calc question evaluation
    data_file = Path(__file__).parent / "test_data/complex_jexl_context.json"
    assert data_file.exists()
    call_command("loaddata", str(data_file))
    return Form.objects.get(slug="demo-formular-1")


@pytest.fixture
def complex_jexl_doc(complex_jexl_form):
    """Return a document with a few questions answered.

    The structure is as follows:

    FieldSet(demo-formular-1)
       Field(demo-outer-table-question-1, None)
          FieldSet(demo-table-form-1)
             Field(demo-table-question-1, 3)
             Field(demo-table-question-2, 1)
          FieldSet(demo-table-form-1)
             Field(demo-table-question-1, 20)
             Field(demo-table-question-2, 100)
       Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)
       Field(demo-outer-table-question-2, None)
    """
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

    assert structure.list_document_structure(doc, method=repr) == [
        " FieldSet(q=(root), f=demo-formular-1)",
        "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=3)",
        "          ValueField(q=demo-table-question-2, v=1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=20)",
        "          ValueField(q=demo-table-question-2, v=100)",
        "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
        "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
    ]


def test_update_calc_dependency_inside_table(
    transactional_db, complex_jexl_form, complex_jexl_doc
):
    doc, row1, row2 = complex_jexl_doc

    assert structure.list_document_structure(doc, method=repr) == [
        " FieldSet(q=(root), f=demo-formular-1)",
        "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=3)",
        "          ValueField(q=demo-table-question-2, v=1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=20)",
        "          ValueField(q=demo-table-question-2, v=100)",
        "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
        "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
    ]
    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row1, value=30
    )
    assert (
        structure.list_document_structure(doc, method=repr)
        == [
            " FieldSet(q=(root), f=demo-formular-1)",
            "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "          ValueField(q=demo-table-question-1, v=30)",  # this was set
            "          ValueField(q=demo-table-question-2, v=100)",  # should have been recalc'd
            "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "          ValueField(q=demo-table-question-1, v=20)",
            "          ValueField(q=demo-table-question-2, v=100)",
            "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
            "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
        ]
    )

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row1, value=3
    )
    assert structure.list_document_structure(doc, method=repr) == [
        " FieldSet(q=(root), f=demo-formular-1)",
        "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=3)",  # updated again
        "          ValueField(q=demo-table-question-2, v=1)",  # recalculated again
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=20)",
        "          ValueField(q=demo-table-question-2, v=100)",
        "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
        "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row2, value=40
    )
    assert (
        structure.list_document_structure(doc, method=repr)
        == [
            " FieldSet(q=(root), f=demo-formular-1)",
            "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "          ValueField(q=demo-table-question-1, v=3)",
            "          ValueField(q=demo-table-question-2, v=1)",
            "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
            "          ValueField(q=demo-table-question-1, v=40)",  # updated here
            "          ValueField(q=demo-table-question-2, v=100)",  # recalculated , same value
            "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
            "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
        ]
    )

    api.save_answer(
        Question.objects.get(pk="demo-table-question-1"), document=row2, value=2
    )
    assert structure.list_document_structure(doc, method=repr) == [
        " FieldSet(q=(root), f=demo-formular-1)",
        "    RowSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=3)",
        "          ValueField(q=demo-table-question-2, v=1)",
        "       FieldSet(q=demo-outer-table-question-1, f=demo-table-form-1)",
        "          ValueField(q=demo-table-question-1, v=2)",  # updated
        "          ValueField(q=demo-table-question-2, v=1)",  # recalculated
        "    ValueField(q=demo-outer-question-1, v=demo-outer-question-1-outer-option-a)",
        "    RowSet(q=demo-outer-table-question-2, f=demo-table-form-2)",
    ]


def test_update_calc_dependency_inside_table_with_outer_reference(
    transactional_db, complex_jexl_form, complex_jexl_doc
):
    doc, _, _ = complex_jexl_doc

    assert structure.list_document_structure(doc) == [
        " FieldSet(demo-formular-1)",
        "    RowSet(demo-table-form-1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 3)",
        "          Field(demo-table-question-2, 1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 20)",
        "          Field(demo-table-question-2, 100)",
        "    Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "    RowSet(demo-table-form-2)",
    ]

    # TODO: This implementation corresponds to the current frontend logic, this
    # might change so that table row documents are attached on creation
    new_table_doc = api.save_document(form=Form.objects.get(pk="demo-table-form-2"))

    assert structure.list_document_structure(new_table_doc) == [
        " FieldSet(demo-table-form-2)",
        "    Field(demo-table-question-outer-ref-hidden, None)",
        "    Field(demo-table-question-outer-ref-calc, None)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-outer-ref-hidden"),
        document=new_table_doc,
        value=30,
    )

    # We did save a value of 30, but the `outer-ref-hidden` refers to
    # an out-of-reach question in it's `is_hidden` expression, thus is
    # considered hidden itself. In turn, the `outer-ref-calc` can't calculate
    # either.
    assert structure.list_document_structure(new_table_doc) == [
        " FieldSet(demo-table-form-2)",
        "    Field(demo-table-question-outer-ref-hidden, None)",
        "    Field(demo-table-question-outer-ref-calc, None)",
    ]

    # We now attach the table row to the main document, which should make
    # it fully calculated, as the outer questions referenced from within
    # the table are now reachable.
    api.save_answer(
        question=Question.objects.get(pk="demo-outer-table-question-2"),
        document=doc,
        value=[new_table_doc.pk],
    )

    assert structure.list_document_structure(doc) == [
        " FieldSet(demo-formular-1)",
        "    RowSet(demo-table-form-1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 3)",
        "          Field(demo-table-question-2, 1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 20)",
        "          Field(demo-table-question-2, 100)",
        "    Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "    RowSet(demo-table-form-2)",
        "       FieldSet(demo-table-form-2)",
        "          Field(demo-table-question-outer-ref-hidden, 30)",
        "          Field(demo-table-question-outer-ref-calc, 30)",
    ]

    api.save_answer(
        Question.objects.get(pk="demo-table-question-outer-ref-hidden"),
        document=new_table_doc,
        value=20,
    )

    assert structure.list_document_structure(doc) == [
        " FieldSet(demo-formular-1)",
        "    RowSet(demo-table-form-1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 3)",
        "          Field(demo-table-question-2, 1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 20)",
        "          Field(demo-table-question-2, 100)",
        "    Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "    RowSet(demo-table-form-2)",
        "       FieldSet(demo-table-form-2)",
        "          Field(demo-table-question-outer-ref-hidden, 20)",
        "          Field(demo-table-question-outer-ref-calc, 20)",
    ]


def test_structure_caching(transactional_db, complex_jexl_form, complex_jexl_doc):
    doc, _, _ = complex_jexl_doc

    hit_count_before = structure.object_local_memoise.hit_count
    miss_count_before = structure.object_local_memoise.miss_count

    assert structure.list_document_structure(doc) == [
        " FieldSet(demo-formular-1)",
        "    RowSet(demo-table-form-1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 3)",
        "          Field(demo-table-question-2, 1)",
        "       FieldSet(demo-table-form-1)",
        "          Field(demo-table-question-1, 20)",
        "          Field(demo-table-question-2, 100)",
        "    Field(demo-outer-question-1, demo-outer-question-1-outer-option-a)",
        "    RowSet(demo-table-form-2)",
    ]

    # Note: If those fail, just update the counts. I'm more interested in a
    # rather rough overview of cache hits, not the exact numbers. Changing the
    # caching will affect hese numbers.
    assert structure.object_local_memoise.hit_count - hit_count_before == 46
    assert structure.object_local_memoise.miss_count - miss_count_before == 54
