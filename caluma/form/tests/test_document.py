import pytest
from graphql_relay import to_global_id

from .. import serializers
from ...core.relay import extract_global_id
from ...core.tests import extract_serializer_input_fields
from ...form.models import Answer, Question


@pytest.mark.parametrize(
    "question__type,answer__value",
    [
        (Question.TYPE_INTEGER, 1),
        (Question.TYPE_FLOAT, 2.1),
        (Question.TYPE_TEXT, "somevalue"),
        (Question.TYPE_CHECKBOX, ["somevalue", "anothervalue"]),
        (Question.TYPE_TABLE, None),
    ],
)
def test_query_all_documents(
    db,
    snapshot,
    form_question,
    form,
    document,
    document_factory,
    answer_document,
    answer,
    schema_executor,
):
    query = """
        query AllDocumentsQuery($search: String) {
          allDocuments(search: $search) {
            edges {
              node {
                createdByUser
                answers {
                  edges {
                    node {
                      __typename
                      question {
                        slug
                        label
                      }
                      ... on StringAnswer {
                        string_value: value
                      }
                      ... on IntegerAnswer {
                        integer_value: value
                      }
                      ... on ListAnswer {
                        list_value: value
                      }
                      ... on FloatAnswer {
                        float_value: value
                      }
                      ... on TableAnswer {
                        table_value: value {
                          form {
                            slug
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    search = isinstance(answer.value, list) and " ".join(answer.value) or answer.value
    result = schema_executor(query, variables={"search": search})
    assert not result.errors
    snapshot.assert_match(result.data)


def test_complex_document_query_performance(
    db,
    schema_executor,
    document,
    form,
    form_question_factory,
    question_factory,
    answer_factory,
    question_option_factory,
    django_assert_num_queries,
):
    answers = answer_factory.create_batch(5, document=document)
    for answer in answers:
        form_question_factory(question=answer.question, form=form)
    checkbox_question = question_factory(type=Question.TYPE_CHECKBOX)
    form_question_factory(question=checkbox_question, form=form)
    question_option_factory.create_batch(10, question=checkbox_question)
    answer_factory(question=checkbox_question)

    query = """
        query ($id: ID!) {
          allDocuments(id: $id) {
            edges {
              node {
                ...FormDocument
              }
            }
          }
        }

        fragment FormDocument on Document {
          id
          answers {
            edges {
              node {
                ...FieldAnswer
              }
            }
          }
          form {
            slug
            questions {
              edges {
                node {
                  ...FieldQuestion
                }
              }
            }
          }
        }

        fragment FieldAnswer on Answer {
          id
          question {
            slug
          }
          ... on StringAnswer {
            stringValue: value
          }
          ... on IntegerAnswer {
            integerValue: value
          }
          ... on FloatAnswer {
            floatValue: value
          }
          ... on ListAnswer {
            listValue: value
          }
        }

        fragment FieldQuestion on Question {
          slug
          label
          isRequired
          isHidden
          ... on TextQuestion {
            textMaxLength: maxLength
          }
          ... on TextareaQuestion {
            textareaMaxLength: maxLength
          }
          ... on IntegerQuestion {
            integerMinValue: minValue
            integerMaxValue: maxValue
          }
          ... on FloatQuestion {
            floatMinValue: minValue
            floatMaxValue: maxValue
          }
          ... on RadioQuestion {
            radioOptions: options {
              edges {
                node {
                  slug
                  label
                }
              }
            }
          }
          ... on CheckboxQuestion {
            checkboxOptions: options {
              edges {
                node {
                  slug
                  label
                }
              }
            }
          }
        }
    """

    with django_assert_num_queries(10):
        result = schema_executor(query, variables={"id": str(document.pk)})
    assert not result.errors


def test_query_all_documents_filter_answers_by_question(
    db, snapshot, document, answer, question, answer_factory, schema_executor
):
    answer_factory(document=document)

    query = """
        query AllDocumentsQuery($question: ID!) {
          allDocuments {
            edges {
              node {
                answers(question: $question) {
                  edges {
                    node {
                      id
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variables={"question": question.slug})
    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 1
    result_document = result.data["allDocuments"]["edges"][0]["node"]
    assert len(result_document["answers"]["edges"]) == 1
    result_answer = result_document["answers"]["edges"][0]["node"]
    assert extract_global_id(result_answer["id"]) == str(answer.id)


def test_save_document(db, snapshot, document, schema_executor):
    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
          saveDocument(input: $input) {
            document {
                form {
                    slug
                }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.DocumentSerializer, document
        )
    }
    result = schema_executor(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value,mutation,success",
    [
        (Question.TYPE_INTEGER, {}, 1, "SaveDocumentIntegerAnswer", True),
        (
            Question.TYPE_INTEGER,
            {"min_value": 100},
            1,
            "SaveDocumentIntegerAnswer",
            False,
        ),
        (Question.TYPE_FLOAT, {}, 2.1, "SaveDocumentFloatAnswer", True),
        (
            Question.TYPE_FLOAT,
            {"min_value": 100.0},
            1,
            "SaveDocumentFloatAnswer",
            False,
        ),
        (Question.TYPE_TEXT, {}, "Test", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_TABLE, {}, None, "SaveDocumentTableAnswer", True),
        (Question.TYPE_TEXTAREA, {}, "Test", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXTAREA,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_CHECKBOX, {}, ["option-slug"], "SaveDocumentListAnswer", True),
        (
            Question.TYPE_CHECKBOX,
            {},
            ["option-slug", "option-invalid-slug"],
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_RADIO, {}, "option-slug", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_RADIO,
            {},
            "invalid-option-slug",
            "SaveDocumentStringAnswer",
            False,
        ),
    ],
)
def test_save_document_answer(
    db,
    snapshot,
    question,
    answer,
    mutation,
    question_option,
    document_factory,
    answer_factory,
    answer_document_factory,
    success,
    schema_executor,
    delete_answer,
):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            answer {{
              ... on StringAnswer {{
                stringValue: value
              }}
              ... on IntegerAnswer {{
                integerValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
              ... on FloatAnswer {{
                floatValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
              ... on TableAnswer {{
                table_value: value {{
                  form {{
                    slug
                  }}
                }}
              }}
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    if question.type == Question.TYPE_TABLE:
        documents = document_factory.create_batch(2, form=question.row_form)
        # create a subtree
        document_answer = answer_factory()
        documents[0].answers.add(document_answer)
        answer_document_factory(answer=answer, document=documents[0])

        inp["input"]["value"] = [str(document.pk) for document in documents]

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    result = schema_executor(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


def test_save_document_table_answer_invalid_row_form(
    db, schema_executor, answer, document_factory
):
    query = """
        mutation SaveDocumentTableAnswer($input: SaveDocumentTableAnswerInput!) {
            saveDocumentTableAnswer(input: $input) {
                clientMutationId
            }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    inp["input"]["value"] = [
        str(document.pk) for document in document_factory.create_batch(1)
    ]
    result = schema_executor(query, variables=inp)
    assert result.errors


@pytest.mark.parametrize("answer__value", [1.1])
def test_query_answer_node(db, answer, schema_executor):
    global_id = to_global_id("FloatAnswer", answer.pk)

    node_query = """
    query AnswerNode($id: ID!) {
      node(id: $id) {
        ... on FloatAnswer {
            value
        }
      }
    }
    """

    result = schema_executor(node_query, variables={"id": global_id})
    assert not result.errors
