from uuid import UUID

import pytest
from django.utils import timezone

from .. import models


@pytest.mark.parametrize("question__type", [models.Question.TYPE_TEXT])
def test_history(db, question, document, schema_executor, admin_schema_executor):
    query = """
        mutation MyStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer (input: $input) {
            answer {
              id
            }
          }
        }
    """

    result = admin_schema_executor(
        query,
        variable_values={
            "input": {
                "question": str(question.pk),
                "value": "dolor",
                "document": str(document.pk),
            }
        },
    )
    assert not result.errors
    assert (
        models.Answer.history.get(value="dolor").history_user
        == admin_schema_executor.keywords["context_value"].user.username
    )

    query = """
            mutation MyStringAnswer($input: SaveDocumentStringAnswerInput!) {
              saveDocumentStringAnswer (input: $input) {
                answer {
                  id
                }
              }
            }
        """

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "question": str(question.pk),
                "value": "sit",
                "document": str(document.pk),
            }
        },
    )
    assert not result.errors
    assert models.Answer.history.count() == 2
    history = models.Answer.history.all()
    assert (
        history[1].history_user
        == admin_schema_executor.keywords["context_value"].user.username
    )
    assert history[1].value == "dolor"

    assert history[0].history_user == "AnonymousUser"
    assert history[0].value == "sit"


def test_document_as_of(
    db,
    form_factory,
    form_question_factory,
    answer_factory,
    document_factory,
    snapshot,
    schema_executor,
    admin_schema_executor,
):
    f = form_factory(slug="root-form")
    document = document_factory(form=f, id=UUID("890ca108-d93d-4725-9066-7d0bddad8230"))

    q1 = form_question_factory(
        question__type=models.Question.TYPE_TEXT,
        question__slug="test_question1",
        form=f,
    )
    save_answer_query = """
        mutation saveAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            clientMutationId
          }
        }
    """

    input = {
        "document": document.pk,
        "value": "first admin - revision 1",
        "question": q1.question.slug,
    }

    result = admin_schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    timestamp1 = timezone.now()

    input["value"] = "second admin - revision 2 - not queried"
    result = admin_schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors

    input["value"] = "first anon - revision 3"
    result = schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    timestamp2 = timezone.now()

    input["value"] = "second anon - revision 4"
    result = schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    timestamp3 = timezone.now()

    document.answers.get(question=q1.question).delete()

    historical_query = """
        query documentAsOf($id: ID!, $asOf: DateTime!) {
          documentAsOf (id: $id, asOf: $asOf) {
            meta
            documentId
            historicalAnswers (asOf: $asOf) {
              edges {
                node {
                  ...on HistoricalStringAnswer {
                    __typename
                    value
                    historyUserId
                  }
                }
              }
            }
          }
        }
    """

    variables = {"id": document.pk, "asOf": timestamp1}

    result = admin_schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    snapshot.assert_match(result.data)

    variables["asOf"] = timestamp2
    result = admin_schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    snapshot.assert_match(result.data)

    variables["asOf"] = timestamp3
    result = admin_schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    snapshot.assert_match(result.data)

    variables["asOf"] = timezone.make_aware(timezone.datetime(1900, 9, 15))
    result = admin_schema_executor(historical_query, variable_values=variables)
    assert result.errors


def test_historical_file_answer(
    db,
    minio_mock,
    form_factory,
    document_factory,
    form_question_factory,
    schema_executor,
):
    f = form_factory(slug="root-form")
    document = document_factory(form=f)

    q1 = form_question_factory(
        question__type=models.Question.TYPE_FILE,
        question__slug="test_question1",
        form=f,
    )
    save_answer_query = """
            mutation saveAnswer($input: SaveDocumentFileAnswerInput!) {
              saveDocumentFileAnswer(input: $input) {
                clientMutationId
              }
            }
        """

    input = {
        "document": document.pk,
        "value": "my_file - rev 1",
        "question": q1.question.slug,
    }

    result = schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    hist_file_1 = models.File.history.first()
    timestamp1 = timezone.now()

    input["value"] = "my_file - rev 2"
    result = schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    hist_file_2 = models.File.history.first()
    timestamp2 = timezone.now()

    input["value"] = "my_file - rev 3"
    result = schema_executor(save_answer_query, variable_values={"input": input})
    assert not result.errors
    file3 = document.answers.get(question=q1.question).file

    minio_mock.copy_object.assert_called()
    minio_mock.remove_object.assert_called()

    historical_query = """
            query documentAsOf($id: ID!, $asOf: DateTime!) {
              documentAsOf (id: $id, asOf: $asOf) {
                historicalAnswers (asOf: $asOf) {
                  edges {
                    node {
                      ...on HistoricalFileAnswer {
                        __typename
                        historyUserId
                        value (asOf: $asOf) {
                          name
                          downloadUrl
                          historyUserId
                          historyType
                          historicalAnswer {
                            id
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
        """

    variables = {"id": document.pk, "asOf": timestamp1}
    result = schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"]["value"][
            "downloadUrl"
        ]
        == f"http://minio/download-url/{hist_file_1.pk}_{hist_file_1.name}"
    )

    variables["asOf"] = timestamp2
    result = schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"]["value"][
            "downloadUrl"
        ]
        == f"http://minio/download-url/{hist_file_2.pk}_{hist_file_2.name}"
    )

    # This is the newest revision, so the uuid in the downloadUri must be the one
    # from the actual file and not from the history record.
    variables["asOf"] = timezone.now()
    result = schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"]["value"][
            "downloadUrl"
        ]
        == f"http://minio/download-url/{file3.pk}_{file3.name}"
    )


def test_historical_table_answer(
    db,
    form_factory,
    document_factory,
    form_question_factory,
    answer_factory,
    answer_document_factory,
    schema_executor,
    snapshot,
):
    f = form_factory(slug="root-form")
    row_f = form_factory(slug="row-form")

    q_main = form_question_factory(
        question__type=models.Question.TYPE_TABLE,
        question__slug="test_table_question1",
        question__row_form=row_f,
        form=f,
    )
    main_document = document_factory(form=f)

    q_row = form_question_factory(
        question__type=models.Question.TYPE_TEXT,
        question__slug="test_row_question1",
        form=row_f,
    )
    row1_document = document_factory(form=row_f)
    answer_factory(
        question=q_row.question, document=row1_document, value="first row value"
    )

    row2_document = document_factory(form=row_f)
    answer = answer_factory(
        question=q_row.question, document=row2_document, value="second row value"
    )

    ad = answer_document_factory(
        answer__question=q_main.question,
        answer__document=main_document,
        document=row1_document,
        sort=0,
    )
    answer_document_factory(answer=ad.answer, document=row2_document, sort=1)

    timestamp_init = timezone.now()

    answer.delete()
    timestamp_2 = timezone.now()

    historical_query = """
        query documentAsOf($id: ID!, $asOf1: DateTime!, $asOf2: DateTime!) {
          d1: documentAsOf (id: $id, asOf: $asOf1) {
            historicalAnswers (asOf: $asOf1) {
              edges {
                node {
                  ...on HistoricalTableAnswer {
                    __typename
                    value (asOf: $asOf1) {
                      historicalAnswers (asOf: $asOf1) {
                        edges {
                          node {
                            ...on HistoricalStringAnswer {
                              value
                              historyType
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
          d2: documentAsOf (id: $id, asOf: $asOf2) {
            historicalAnswers (asOf: $asOf2) {
              edges {
                node {
                  ...on HistoricalTableAnswer {
                    __typename
                    value (asOf: $asOf2) {
                      historicalAnswers (asOf: $asOf2) {
                        edges {
                          node {
                            ...on HistoricalStringAnswer {
                              value
                              historyType
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

    variables = {"id": main_document.pk, "asOf1": timestamp_init, "asOf2": timestamp_2}
    result = schema_executor(historical_query, variable_values=variables)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_history_answer_type(
    db,
    answer_factory,
    form_question_factory,
    document_factory,
    form,
    schema_executor,
    admin_schema_executor,
):
    """Test that the answer type is resolved correctly through history.

    The answer type should resolve to the type of the question of the given time (as_of).
    Resolve type correctly even if the question type of a given question-slug changed.
    """
    document = document_factory(form=form)

    old_question = form_question_factory(
        question__type=models.Question.TYPE_TEXT, form=form
    ).question

    # create first answer type text
    query = """
        mutation saveAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            clientMutationId
          }
        }
    """

    result = admin_schema_executor(
        query,
        variable_values={
            "input": {
                "question": str(old_question.pk),
                "value": "some text answer",
                "document": str(document.pk),
            }
        },
    )

    old_date = timezone.now()
    old_answer = models.Answer.objects.get()

    historical_answer = old_answer.history.first()
    historical_question = old_question.history.first()

    # delete old_question and create one with identical slug but different type
    old_question.delete()
    new_question = form_question_factory(
        form=form,
        question__slug=historical_question.slug,
        question__type=models.Question.TYPE_INTEGER,
    ).question

    query = """
        mutation MyIntegerAnswer($input: SaveDocumentIntegerAnswerInput!) {
          saveDocumentIntegerAnswer (input: $input) {
            answer {
              id
            }
          }
        }
    """

    # add new integer answer
    result = admin_schema_executor(
        query,
        variable_values={
            "input": {
                "question": str(new_question.pk),
                "value": 123,
                "document": str(document.pk),
            }
        },
    )
    assert not result.errors

    historical_query = """
        query documentAsOf($id: ID!, $asOf: DateTime!) {
          documentAsOf (id: $id, asOf: $asOf) {
            meta
            documentId
            historicalAnswers (asOf: $asOf) {
              edges {
                node {
                  __typename
                  ...on HistoricalStringAnswer {
                    stringValue: value
                  }
                  ...on HistoricalIntegerAnswer {
                    integerValue: value
                  }
                }
              }
            }
          }
        }
    """

    # old date resolves to the string value
    variables = {"id": document.pk, "asOf": old_date}
    result = admin_schema_executor(historical_query, variable_values=variables)

    assert not result.errors
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"][
            "stringValue"
        ]
        == historical_answer.value
    )
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"][
            "__typename"
        ]
        == "HistoricalStringAnswer"
    )

    # current date resolves to integer value
    variables = {"id": document.pk, "asOf": timezone.now()}
    result = admin_schema_executor(historical_query, variable_values=variables)

    assert not result.errors
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"][
            "integerValue"
        ]
        == 123
    )
    assert (
        result.data["documentAsOf"]["historicalAnswers"]["edges"][0]["node"][
            "__typename"
        ]
        == "HistoricalIntegerAnswer"
    )
