from ...caluma_core.relay import extract_global_id
from .. import models


def test_root_document_filter(
    schema_executor,
    db,
    form_factory,
    form_question_factory,
    document_factory,
    answer_factory,
):
    # build up our form first
    top_form = form_factory()
    top_question = form_question_factory.create(
        form=top_form,
        question__slug="top_question",
        question__type=models.Question.TYPE_TEXT,
    ).question
    subform_question = form_question_factory.create(
        form=top_form,
        question__slug="subform-question",
        question__type=models.Question.TYPE_FORM,
        question__sub_form__slug="subform",
    ).question

    sub_questions = [
        form_question_factory(
            question__slug="foo",
            question__type=models.Question.TYPE_TEXT,
            form=subform_question.sub_form,
        ).question,
        form_question_factory(
            question__slug="bar",
            question__type=models.Question.TYPE_TEXT,
            form=subform_question.sub_form,
        ).question,
    ]

    document1 = document_factory(form=top_form)
    document2 = document_factory(form=top_form, family=document1)
    document3 = document_factory(form=top_form)

    for d in [document1, document2]:
        for question in sub_questions:
            answer_factory(question=question, document=d, value="hello")

    answer_factory(question=top_question, document=document3, value="foo")

    # fetch documents, see if subdocuments are included
    query = """
        query asdf ($root: ID!) {
          allDocuments(rootDocument: $root) {
            edges {
              node {
                id
              }
            }
          }
        }
    """
    variables = {"root": str(document1.id)}

    result = schema_executor(query, variable_values=variables)
    assert not result.errors
    result_ids = [
        extract_global_id(doc["node"]["id"])
        for doc in result.data["allDocuments"]["edges"]
    ]

    assert sorted(result_ids) == sorted([str(document1.id), str(document2.id)])
