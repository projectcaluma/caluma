import json
from datetime import datetime

import minio.error
import pytest
from django.utils.dateparse import parse_date
from graphql_relay import to_global_id

from caluma.caluma_core.tests import extract_serializer_input_fields
from caluma.caluma_core.validations import BaseValidation

from .. import api, models, serializers
from ..models import Answer, Question


@pytest.mark.parametrize(
    "question__type,answer__value", [(models.Question.TYPE_INTEGER, 23)]
)
def test_remove_answer(db, snapshot, question, answer, schema_executor):
    query = """
        mutation RemoveAnswer($input: RemoveAnswerInput!) {
          removeAnswer(input: $input) {
            answer {
              id
              meta
              __typename
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"answer": str(answer.pk)}}
    )

    assert not result.errors
    with pytest.raises(models.Answer.DoesNotExist):
        answer.refresh_from_db()

    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "question__type,answer__value", [(models.Question.TYPE_INTEGER, 23)]
)
def test_remove_default_answer(db, snapshot, question, answer, schema_executor):
    query = """
        mutation RemoveDefaultAnswer($input: RemoveDefaultAnswerInput!) {
          removeDefaultAnswer(input: $input) {
            question {
              id
              meta
              __typename
            }
            clientMutationId
          }
        }
    """

    question.default_answer = answer
    question.save()

    result = schema_executor(
        query, variable_values={"input": {"question": str(question.pk)}}
    )

    assert not result.errors
    with pytest.raises(models.Answer.DoesNotExist):
        answer.refresh_from_db()

    snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,answer__value,answer__date,mutation,success",
    [
        (Question.TYPE_INTEGER, 1, None, "SaveDefaultIntegerAnswer", True),
        (Question.TYPE_FLOAT, 2.1, None, "SaveDefaultFloatAnswer", True),
        (Question.TYPE_TEXT, "Test", None, "SaveDefaultStringAnswer", True),
        (Question.TYPE_TEXTAREA, "Test", None, "SaveDefaultStringAnswer", True),
        (Question.TYPE_CHOICE, "option-slug", None, "SaveDefaultStringAnswer", True),
        (
            Question.TYPE_MULTIPLE_CHOICE,
            ["option-slug"],
            None,
            "SaveDefaultListAnswer",
            True,
        ),
        (Question.TYPE_DYNAMIC_CHOICE, "5.5", None, "SaveDefaultStringAnswer", False),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            [],
            None,
            "SaveDefaultListAnswer",
            False,
        ),
        (Question.TYPE_DATE, None, "2019-02-22", "SaveDefaultDateAnswer", True),
        (Question.TYPE_FILE, None, None, "SaveDefaultFileAnswer", False),
        (Question.TYPE_TABLE, None, None, "SaveDefaultTableAnswer", True),
    ],
)
def test_save_default_answer_graphql(
    db,
    snapshot,
    question,
    answer,
    mutation,
    question_option,
    document_factory,
    answer_factory,
    answer_document_factory,
    question_factory,
    success,
    schema_executor,
    delete_answer,
    admin_user,
):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            answer {{
              __typename
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
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveDefaultAnswerSerializer, answer
        )
    }

    if question.type == Question.TYPE_TABLE:
        documents = document_factory.create_batch(2, form=question.row_form)
        # create a subtree
        sub_question = question_factory(type=Question.TYPE_TEXT)
        document_answer = answer_factory(question=sub_question)
        documents[0].answers.add(document_answer)
        answer_document_factory(answer=answer, document=documents[0])

        inp["input"]["value"] = [str(document.pk) for document in documents]

    if question.type == Question.TYPE_DATE:
        inp["input"]["value"] = answer.date
        answer.value = None
        answer.save()

    question.default_answer = answer
    question.save()

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success

    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize("delete_answer", [True, False])
@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,answer__value,answer__date,success",
    [
        (Question.TYPE_INTEGER, 1, None, True),
        (Question.TYPE_FLOAT, 2.1, None, True),
        (Question.TYPE_TEXT, "Test", None, True),
        (Question.TYPE_TEXTAREA, "Test", None, True),
        (Question.TYPE_CHOICE, "option-slug", None, True),
        (Question.TYPE_MULTIPLE_CHOICE, ["option-slug"], None, True),
        (Question.TYPE_DYNAMIC_CHOICE, "5.5", None, False),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, [], None, False),
        (Question.TYPE_DATE, None, "2019-02-22", True),
        (Question.TYPE_FILE, None, None, False),
        (Question.TYPE_TABLE, None, None, True),
    ],
)
def test_save_default_answer_python_api(
    db,
    snapshot,
    question,
    answer,
    question_option,
    document_factory,
    answer_factory,
    answer_document_factory,
    question_factory,
    success,
    delete_answer,
    admin_user,
):
    inp = extract_serializer_input_fields(
        serializers.SaveDefaultAnswerSerializer, answer
    )

    if question.type == Question.TYPE_TABLE:
        documents = document_factory.create_batch(2, form=question.row_form)
        # create a subtree
        sub_question = question_factory(type=Question.TYPE_TEXT)
        document_answer = answer_factory(question=sub_question)
        documents[0].answers.add(document_answer)
        answer_document_factory(answer=answer, document=documents[0])

        inp["value"] = [str(document.pk) for document in documents]

    if question.type == Question.TYPE_DATE:
        inp["value"] = answer.date
        answer.value = None
        answer.save()

        if success:
            inp["value"] = parse_date(inp["value"])

    question.default_answer = answer
    question.save()

    if delete_answer:
        # delete answer to force create test instead of update
        Answer.objects.filter(pk=answer.pk).delete()

    if success:
        answer = api.save_default_answer(question, user=admin_user, value=inp["value"])
        snapshot.assert_match(answer)
    else:
        with pytest.raises(Exception):
            api.save_default_answer(question, user=admin_user, value=inp["value"])


@pytest.mark.parametrize("question__type,answer__value", [(Question.TYPE_FLOAT, 0.1)])
def test_save_calculated_dependency_default_answer(
    db, snapshot, question, answer, question_factory, admin_user
):
    question_factory(
        type=Question.TYPE_CALCULATED_FLOAT,
        calc_expression=f"'{question.slug}'|answer * 10",
    )

    inp = extract_serializer_input_fields(
        serializers.SaveDefaultAnswerSerializer, answer
    )

    question.default_answer = answer
    question.save()

    answer = api.save_default_answer(question, user=admin_user, value=inp["value"])
    snapshot.assert_match(answer)


@pytest.mark.parametrize(
    "question__type,answer__value", [(models.Question.TYPE_TEXT, "foo")]
)
def test_delete_question_with_default(db, question, answer):
    question.default_answer = answer
    question.save()
    question.delete()

    with pytest.raises(models.Answer.DoesNotExist):
        answer.refresh_from_db()

    assert models.Answer.history.count() == 2
    assert all(
        h.history_question_type == question.type for h in models.Answer.history.all()
    )


@pytest.mark.parametrize("question__type", [Question.TYPE_TEXT])
def test_validation_class_save_document_answer(db, mocker, answer, schema_executor):
    class CustomValidation(BaseValidation):
        def validate(self, mutation, data, info):
            data["value"] += " (validated)"
            return data

    mocker.patch(
        "caluma.caluma_form.serializers.SaveAnswerSerializer.validation_classes",
        [CustomValidation],
    )

    query = """
        mutation saveDocumentStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            answer {
              __typename
              ... on StringAnswer {
                stringValue: value
              }
            }
            clientMutationId
          }
        }
    """

    variables = {
        "input": {
            "document": to_global_id("StringAnswer", answer.document.pk),
            "question": to_global_id("StringAnswer", answer.question.pk),
            "value": "Test",
        }
    }

    result = schema_executor(query, variable_values=variables)

    assert (
        result.data["saveDocumentStringAnswer"]["answer"]["stringValue"]
        == "Test (validated)"
    )


@pytest.mark.parametrize("question__type", ["file"])
def test_file_answer_metadata(db, answer, schema_executor, minio_mock):
    query = """
        query ans($id: ID!) {
            node(id:$id) {
                ... on FileAnswer {
                    fileValue: value {
                        name
                        downloadUrl
                        metadata
                    }
                }
            }
        }
    """
    vars = {"id": to_global_id("FileAnswer", str(answer.pk))}

    # before "upload"
    old_stat = minio_mock.stat_object.return_value
    minio_mock.stat_object.side_effect = minio.error.S3Error(
        "NoSuchKey",
        "object does not exist",
        resource="bla",
        request_id=134,
        host_id="minio",
        response="bla",
    )

    # Before upload, no metadata is available
    result = schema_executor(query, variable_values=vars)
    assert not result.errors
    assert result.data["node"]["fileValue"]["metadata"] is None

    # After "upload", metadata should contain some useful data
    minio_mock.stat_object.return_value = old_stat
    minio_mock.stat_object.side_effect = None

    result = schema_executor(query, variable_values=vars)
    assert not result.errors

    # Make sure all the values (especially in metadata) are JSON serializable.
    # This is something the schema_executor doesn't test, but may bite us in prod
    metadata = result.data["node"]["fileValue"]["metadata"]
    assert json.dumps(metadata)

    # Ensure some of the important properties having the right types,
    # and being correctly parseable
    assert isinstance(metadata["last_modified"], str)
    assert isinstance(metadata["size"], int)
    assert all(isinstance(m, str) for m in metadata["metadata"].values())
    assert datetime.fromisoformat(metadata["last_modified"])
