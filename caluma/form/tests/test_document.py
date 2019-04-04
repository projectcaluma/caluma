import pytest
from graphql_relay import to_global_id

from ...core.relay import extract_global_id
from ...core.tests import extract_serializer_input_fields
from ...form.models import Answer, Question
from .. import serializers


@pytest.mark.parametrize(
    "question__type,answer__value",
    [
        (Question.TYPE_INTEGER, 1),
        (Question.TYPE_FLOAT, 2.1),
        (Question.TYPE_TEXT, "somevalue"),
        (Question.TYPE_MULTIPLE_CHOICE, ["somevalue", "anothervalue"]),
        (Question.TYPE_TABLE, None),
        (Question.TYPE_FILE, "some-file.pdf"),
        (Question.TYPE_FILE, "some-other-file.pdf"),
    ],
)
def test_query_all_documents(
    db,
    snapshot,
    form_question,
    form,
    document,
    document_factory,
    question_factory,
    form_question_factory,
    answer_factory,
    file_factory,
    answer_document,
    answer,
    schema_executor,
    question,
    minio_mock,
    settings,
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
                      ... on DateAnswer {
                        date_value: value
                      }
                      ... on TableAnswer {
                        table_value: value {
                          form {
                            slug
                          }
                        }
                      }
                      ... on FormAnswer {
                        form_value: value {
                          form {
                            slug
                          }
                        }
                      }
                      ... on FileAnswer {
                        fileValue: value {
                          name
                          downloadUrl
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

    if question.type == Question.TYPE_FILE:
        file_question = question_factory(type=Question.TYPE_FILE)
        form_question_factory(question=file_question, form=form)
        answer_factory(
            question=file_question,
            value=None,
            document=document,
            file=file_factory(name="some-file.pdf"),
        )

        if answer.value == "some-other-file.pdf":
            settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False
            minio_mock.bucket_exists.return_value = False

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
    file_factory,
    question_option_factory,
    django_assert_num_queries,
    minio_mock,
):
    answers = answer_factory.create_batch(5, document=document)
    for answer in answers:
        form_question_factory(question=answer.question, form=form)
    multiple_choice_question = question_factory(type=Question.TYPE_MULTIPLE_CHOICE)
    form_question_factory(question=multiple_choice_question, form=form)
    question_option_factory.create_batch(10, question=multiple_choice_question)
    answer_factory(question=multiple_choice_question)
    file_question = question_factory(type=Question.TYPE_FILE)
    form_question_factory(question=file_question, form=form)
    answer_factory(
        question=file_question, value=None, document=document, file=file_factory()
    )

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
          __typename
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
          ... on DateAnswer {
            dateValue: value
          }
          ... on ListAnswer {
            listValue: value
          }
          ... on FileAnswer {
            fileValue: value {
              name
              downloadUrl
            }
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
          ... on ChoiceQuestion {
            choiceOptions: options {
              edges {
                node {
                  slug
                  label
                }
              }
            }
          }
          ... on MultipleChoiceQuestion {
            multipleChoiceOptions: options {
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

    with django_assert_num_queries(11):
        result = schema_executor(query, variables={"id": str(document.pk)})
    assert not result.errors


def test_query_all_documents_filter_answers_by_question(
    db, document, answer, question, answer_factory, schema_executor
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


def test_save_document(db, document, schema_executor):
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
    assert result.data["saveDocument"]["document"]["form"]["slug"] == document.form.slug


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
        (Question.TYPE_DATE, {}, "not a date", "SaveDocumentDateAnswer", False),
        (Question.TYPE_DATE, {}, "2019-02-22", "SaveDocumentDateAnswer", True),
        (Question.TYPE_FILE, {}, None, "SaveDocumentFileAnswer", False),
        (Question.TYPE_FILE, {}, "some-file.pdf", "SaveDocumentFileAnswer", True),
        (Question.TYPE_FILE, {}, "not-exist.pdf", "SaveDocumentFileAnswer", True),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_TABLE, {}, None, "SaveDocumentTableAnswer", True),
        (Question.TYPE_FORM, {}, None, "SaveDocumentFormAnswer", True),
        (Question.TYPE_TEXTAREA, {}, "Test", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXTAREA,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            ["option-slug"],
            "SaveDocumentListAnswer",
            True,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            ["option-slug", "option-invalid-slug"],
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_CHOICE, {}, "option-slug", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_CHOICE,
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
    file_factory,
    success,
    schema_executor,
    delete_answer,
    minio_mock,
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
              ... on DateAnswer {{
                dateValue: value
              }}
              ... on TableAnswer {{
                table_value: value {{
                  form {{
                    slug
                  }}
                }}
              }}
              ... on FormAnswer {{
                form_value: value {{
                  form {{
                    slug
                  }}
                }}
              }}
              ... on FileAnswer {{
                fileValue: value {{
                  name
                  uploadUrl
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
    if question.type == Question.TYPE_FORM:
        document1 = document_factory.create(form=question.row_form)
        document2 = document_factory.create()
        answer.value_document = document2
        answer.save()
        inp["input"]["value"] = document1.pk

    if question.type == Question.TYPE_FILE and answer.value == "some-file.pdf":
        file = file_factory(name="some-file.pdf")
        answer.file = file
        answer.save()
        minio_mock.bucket_exists.return_value = False

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


@pytest.mark.parametrize("question__type", [Question.TYPE_FORM])
def test_save_document_form_answer_invalid_row_form(
    db, schema_executor, answer_factory, question, document_factory
):
    answer = answer_factory.create(question=question)
    query = """
        mutation SaveDocumentFormAnswer($input: SaveDocumentFormAnswerInput!) {
            saveDocumentFormAnswer(input: $input) {
                clientMutationId
            }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    inp["input"]["value"] = str(document_factory.create().pk)
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


def test_create_document_with_children(
    db, form_question_factory, question_factory, schema_executor
):
    sub_form_question = form_question_factory(question__type=Question.TYPE_FORM)
    question = question_factory(
        type=Question.TYPE_FORM, sub_form=sub_form_question.form
    )
    form_question = form_question_factory(question=question)

    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
            saveDocument(input: $input) {
                document {
                    id
                    answers {
                        edges {
                            node {
                                id
                                ... on FormAnswer {
                                    value {
                                        id
                                        answers {
                                            edges {
                                                node {
                                                    id
                                                    ... on FormAnswer {
                                                        value {
                                                            id
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
                }
            }
        }
    """

    inp = {"input": {"form": form_question.form.pk}}
    result = schema_executor(query, variables=inp)
    assert not result.errors
    sub_document = result.data["saveDocument"]["document"]["answers"]["edges"][0][
        "node"
    ]
    assert sub_document["id"]
    assert sub_document["value"]["answers"]["edges"][0]["node"]["id"]
