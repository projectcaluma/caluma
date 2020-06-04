import pytest

from caluma.caluma_form.models import Question

from ..relay import extract_global_id


@pytest.mark.parametrize("question__type", ["text"])
def test_inversible_with_vars(db, schema_executor, document_factory, question):

    doc_a, doc_b, doc_c = (
        document_factory(meta={"foo": "a", "blah": "xxx"}),
        document_factory(meta={"foo": "b", "blah": "xxx"}),
        document_factory(meta={"foo": "c", "blah": "blub"}),
    )

    doc_a.answers.create(question=question, value="44")
    doc_b.answers.create(question=question, value="33")
    doc_c.answers.create(question=question, value="22")

    query = """
        query test_ordering($order: [DocumentOrderSetType]) {
          allDocuments(order: $order) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    doc_a_id = str(doc_a.id)
    doc_b_id = str(doc_b.id)
    doc_c_id = str(doc_c.id)

    def result_ids(result):
        return [
            extract_global_id(n["node"]["id"])
            for n in result.data["allDocuments"]["edges"]
        ]

    def get_ordered(ordering):
        result = schema_executor(query, variable_values={"order": ordering})
        assert not result.errors
        return result_ids(result)

    # ordering by answer value, forward.
    ordered = get_ordered([{"answerValue": question.slug}])
    assert ordered == [doc_c_id, doc_b_id, doc_a_id]

    # ordering by answer value, backward.
    ordered = get_ordered([{"answerValue": question.slug, "direction": "DESC"}])
    assert ordered == [doc_a_id, doc_b_id, doc_c_id]

    # order by meta key "blah" first, which contains the same value twice,
    # then by the answer value, which orders the ambiguity between
    # the first two same-value documents
    ordered = get_ordered(
        [{"meta": "blah"}, {"answerValue": question.slug, "direction": "DESC"}]
    )
    assert ordered == [doc_c_id, doc_a_id, doc_b_id]

    # same, but secondary order goes backwards
    ordered = get_ordered([{"meta": "blah"}, {"answerValue": question.slug}])
    assert ordered == [doc_c_id, doc_b_id, doc_a_id]

    # Just for coverage - sort by attribute
    ordered = get_ordered([{"attribute": "FORM"}])

    assert ordered == [
        str(doc.id)
        for doc in sorted([doc_c, doc_b, doc_a], key=lambda doc: doc.form.slug)
    ]


@pytest.mark.parametrize("direction", ["ASC", "DESC"])
@pytest.mark.parametrize("question__type", [Question.TYPE_TEXT])
def test_order_by_case_document_answer(
    db, schema_executor, work_item_factory, direction, question
):

    w1, w2 = work_item_factory.create_batch(2)

    w1.case.document.answers.create(question=question, value="aa")
    w2.case.document.answers.create(question=question, value="bb")

    assert w1.case.id != w2.case.id
    assert w1.case.document.id != w2.case.document.id

    query = """
        query workitems {
          allWorkItems(order: [{caseDocumentAnswer: "%s", direction: %s}]) {
            edges {
              node {
                id
              }
            }
          }
        }
    """ % (
        question.slug,
        direction,
    )

    result = schema_executor(query)

    assert not result.errors
    assert result.data["allWorkItems"]["edges"] is not None
    assert len(result.data["allWorkItems"]["edges"]) == 2

    work_items = [
        extract_global_id(wi["node"]["id"])
        for wi in result.data["allWorkItems"]["edges"]
    ]

    if direction == "ASC":
        assert work_items == [str(w1.id), str(w2.id)]
    else:
        assert work_items == [str(w2.id), str(w1.id)]
