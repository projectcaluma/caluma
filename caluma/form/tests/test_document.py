import pytest
from graphql_relay import to_global_id

from ...core.relay import extract_global_id
from ...core.tests import extract_serializer_input_fields
from ...form.models import Answer, Document, Question
from .. import serializers


@pytest.mark.parametrize(
    "question__type,answer__value,answer__date",
    [
        (Question.TYPE_INTEGER, 1, None),
        (Question.TYPE_FLOAT, 2.1, None),
        (Question.TYPE_TEXT, "somevalue", None),
        (Question.TYPE_MULTIPLE_CHOICE, ["somevalue", "anothervalue"], None),
        (Question.TYPE_TABLE, None, None),
        (Question.TYPE_DATE, None, "2019-02-22"),
        (Question.TYPE_FILE, "some-file.pdf", None),
        (Question.TYPE_FILE, "some-other-file.pdf", None),
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
                          metadata
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

    if question.type == Question.TYPE_FILE:
        if answer.value == "some-other-file.pdf":
            settings.MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = False
            minio_mock.bucket_exists.return_value = False
        answer.file = file_factory(name=answer.value)
        answer.value = None
        answer.save()
        search = answer.file.name

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
              metadata
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

    with django_assert_num_queries(12):
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


@pytest.mark.parametrize("update", [True, False])
def test_save_document(db, document, schema_executor, update):
    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
          saveDocument(input: $input) {
            document {
                form {
                  slug
                }
                id
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

    if not update:
        # not update = create = we don't pass the ID
        del inp["input"]["id"]

    result = schema_executor(query, variables=inp)

    assert not result.errors
    assert result.data["saveDocument"]["document"]["form"]["slug"] == document.form.slug

    same_id = extract_global_id(result.data["saveDocument"]["document"]["id"]) == str(
        document.id
    )

    # if updating, the resulting document must be the same
    assert same_id == update


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value,answer__date,mutation,success",
    [
        (Question.TYPE_INTEGER, {}, 1, None, "SaveDocumentIntegerAnswer", True),
        (
            Question.TYPE_INTEGER,
            {"min_value": 100},
            1,
            None,
            "SaveDocumentIntegerAnswer",
            False,
        ),
        (Question.TYPE_FLOAT, {}, 2.1, None, "SaveDocumentFloatAnswer", True),
        (
            Question.TYPE_FLOAT,
            {"min_value": 100.0},
            1,
            None,
            "SaveDocumentFloatAnswer",
            False,
        ),
        (Question.TYPE_TEXT, {}, "Test", None, "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            "toolong",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_DATE, {}, None, "1900-01-01", "SaveDocumentDateAnswer", False),
        (Question.TYPE_DATE, {}, None, "2019-02-22", "SaveDocumentDateAnswer", True),
        (Question.TYPE_FILE, {}, None, None, "SaveDocumentFileAnswer", False),
        (Question.TYPE_FILE, {}, "some-file.pdf", None, "SaveDocumentFileAnswer", True),
        (Question.TYPE_FILE, {}, "not-exist.pdf", None, "SaveDocumentFileAnswer", True),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            "toolong",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_TABLE, {}, None, None, "SaveDocumentTableAnswer", True),
        (Question.TYPE_FORM, {}, None, None, "SaveDocumentFormAnswer", True),
        (Question.TYPE_TEXTAREA, {}, "Test", None, "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXTAREA,
            {"max_length": 1},
            "toolong",
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            ["option-slug"],
            None,
            "SaveDocumentListAnswer",
            True,
        ),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            {},
            ["option-slug", "option-invalid-slug"],
            None,
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_CHOICE,
            {},
            "option-slug",
            None,
            "SaveDocumentStringAnswer",
            True,
        ),
        (
            Question.TYPE_CHOICE,
            {},
            "invalid-option-slug",
            None,
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
        document = document_factory.create(form=question.sub_form)
        inp["input"]["value"] = document.pk

    if question.type == Question.TYPE_FILE and answer.value == "some-file.pdf":
        file = file_factory(name="some-file.pdf")
        answer.file = file
        answer.save()
        minio_mock.bucket_exists.return_value = False

    if question.type == Question.TYPE_DATE:
        inp["input"]["value"] = answer.date
        answer.value = None
        answer.save()
        # Date format is enforced in the model. So we initially had to use a valid date
        # here we're able to change it:
        if answer.date == "1900-01-01":
            inp["input"]["value"] = "not a date"

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

    doc_id = extract_global_id(result.data["saveDocument"]["document"]["id"])
    doc = Document.objects.get(pk=doc_id)

    # top-level document should be "head of family"
    assert doc.pk == doc.family

    subdoc_id = extract_global_id(
        sub_document["value"]["answers"]["edges"][0]["node"]["value"]["id"]
    )
    sub_doc = Document.objects.get(pk=subdoc_id)

    assert sub_doc.family == doc.family

    assert sub_document["id"]
    assert sub_document["value"]["answers"]["edges"][0]["node"]["id"]
