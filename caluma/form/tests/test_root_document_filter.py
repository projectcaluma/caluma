from ...core.relay import extract_global_id
from .. import models


def test_root_document_filter(
    schema_executor,
    db,
    question,
    form_factory,
    form_question_factory,
    question_factory,
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
        question__slug="subform",
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

    # Now, make a document for it
    result = schema_executor(
        """
            mutation foo ($form_id: ID!){
                saveDocument(input: {form: $form_id}) {
                    document {
                      id
                    }
                }
            }
        """,
        variables={"form_id": top_form.pk},
    )

    document_id = extract_global_id(result.data["saveDocument"]["document"]["id"])
    document = models.Document.objects.get(pk=document_id)
    # just some other question in the tree
    answer_factory(question=top_question, document=document, value="foo")
    ans_subform = document.answers.get(question__slug="subform")

    for question in sub_questions:
        answer_factory(
            question=question, document=ans_subform.value_document, value="hello"
        )

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
    variables = {"root": str(document.id)}

    result = schema_executor(query, variables=variables)
    assert not result.errors
    result_ids = set(
        extract_global_id(doc["node"]["id"])
        for doc in result.data["allDocuments"]["edges"]
    )

    db_doc_ids = set(str(doc.id) for doc in models.Document.objects.all())

    assert db_doc_ids == result_ids
