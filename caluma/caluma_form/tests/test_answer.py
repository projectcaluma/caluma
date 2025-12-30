import json
from datetime import datetime

import minio.error
import pytest
from django.utils.dateparse import parse_date
from graphql_relay import to_global_id
from rest_framework.exceptions import ValidationError

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
        (Question.TYPE_FILES, None, None, "SaveDefaultFilesAnswer", False),
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
        (Question.TYPE_FILES, None, None, False),
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
        with pytest.raises(ValidationError):
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


@pytest.mark.parametrize("question__type", ["files"])
def test_file_answer_metadata(db, answer, schema_executor, minio_mock):
    query = """
        query ans($id: ID!) {
            node(id:$id) {
                ... on FilesAnswer {
                    fileValue: value {
                        name
                        downloadUrl
                        metadata
                    }
                }
            }
        }
    """
    vars = {"id": to_global_id("FilesAnswer", str(answer.pk))}

    # before "upload"
    old_stat = minio_mock.stat_object.return_value
    minio_mock.stat_object.side_effect = minio.error.S3Error(
        code="NoSuchKey",
        message="object does not exist",
        resource="bla",
        request_id=134,
        host_id="minio",
        response="bla",
    )

    # Before upload, no metadata is available
    result = schema_executor(query, variable_values=vars)
    assert not result.errors
    assert result.data["node"]["fileValue"][0]["metadata"] is None

    # After "upload", metadata should contain some useful data
    minio_mock.stat_object.return_value = old_stat
    minio_mock.stat_object.side_effect = None

    result = schema_executor(query, variable_values=vars)
    assert not result.errors

    # Make sure all the values (especially in metadata) are JSON serializable.
    # This is something the schema_executor doesn't test, but may bite us in prod
    metadata = result.data["node"]["fileValue"][0]["metadata"]
    assert json.dumps(metadata)

    # Ensure some of the important properties having the right types,
    # and being correctly parseable
    assert isinstance(metadata["last_modified"], str)
    assert isinstance(metadata["size"], int)
    assert all(isinstance(m, str) for m in metadata["metadata"].values())
    assert datetime.fromisoformat(metadata["last_modified"])


SAVE_DOCUMENT_FILES_ANSWER_QUERY = """
    mutation save ($input: SaveDocumentFilesAnswerInput!) {
        saveDocumentFilesAnswer (input: $input) {
            answer {
                ... on FilesAnswer {
                    value {
                        name
                        uploadUrl
                        id
                    }
                }
            }
        }
    }
"""


@pytest.mark.parametrize("answer__files", [[]])
@pytest.mark.parametrize("question__type", ["files"])
def test_file_answer_mutation_create(db, answer, document, schema_executor, minio_mock):
    # Precondition check
    assert answer.files.count() == 0

    # Initial upload
    result = schema_executor(
        SAVE_DOCUMENT_FILES_ANSWER_QUERY,
        variable_values={
            "input": {
                "document": str(document.pk),
                "question": answer.question.slug,
                "value": [{"name": "some test file.txt"}],
            }
        },
    )
    assert not result.errors
    assert answer.files.count() == 1
    first_file = answer.files.get()
    assert first_file.name == "some test file.txt"


@pytest.mark.parametrize("question__type", ["files"])
def test_file_answer_mutation_add_file(
    db, answer, document, schema_executor, minio_mock
):
    first_file = answer.files.get()
    history_count_before = first_file.history.count()

    # Second request: adding a file
    result = schema_executor(
        SAVE_DOCUMENT_FILES_ANSWER_QUERY,
        variable_values={
            "input": {
                "document": str(document.pk),
                "question": answer.question.slug,
                "value": [
                    {"name": first_file.name, "id": str(first_file.pk)},
                    {"name": "another file.txt"},
                ],
            }
        },
    )
    assert not result.errors
    assert answer.files.count() == 2

    second_file = answer.files.exclude(pk=first_file.pk).get()
    assert second_file.name == "another file.txt"
    # Check that previously-created file wasn't replaced or changed
    assert first_file in answer.files.all()
    assert history_count_before == first_file.history.count()


@pytest.mark.parametrize("question__type", ["files"])
def test_file_answer_mutation_remove_file(
    db, answer, document, schema_executor, minio_mock
):
    # Add a file while removing another (replacing the full
    # files set of an answer)
    assert answer.files.count() == 1
    orig_file = answer.files.get()
    result = schema_executor(
        SAVE_DOCUMENT_FILES_ANSWER_QUERY,
        variable_values={
            "input": {
                "document": str(document.pk),
                "question": answer.question.slug,
                "value": [
                    {"name": "another file.txt"},
                ],
            }
        },
    )
    assert not result.errors
    assert answer.files.count() == 1
    with pytest.raises(type(orig_file).DoesNotExist):
        # This file should be gone
        orig_file.refresh_from_db()


@pytest.mark.parametrize("question__type", ["files"])
def test_file_answer_mutation_update_missing_file(
    db, answer, document, schema_executor, minio_mock
):
    # Add a file while removing another (replacing the full
    # files set of an answer)
    orig_file = answer.files.get()
    orig_file_id = str(orig_file.pk)
    orig_file.delete()

    result = schema_executor(
        SAVE_DOCUMENT_FILES_ANSWER_QUERY,
        variable_values={
            "input": {
                "document": str(document.pk),
                "question": answer.question.slug,
                "value": [
                    {"name": "another file.txt", "id": orig_file_id},
                ],
            }
        },
    )
    assert result.errors
    assert f"File with id={orig_file_id} for given answer not found" in str(
        result.errors[0].args[0]
    )
    assert answer.files.count() == 0


@pytest.mark.parametrize(
    "question_type, answer_value, old_slug, new_slug, expected",
    [
        # retain old value for single choice if it doesn't match the old_slug
        (Question.TYPE_DYNAMIC_CHOICE, None, "test", "new", None),
        (Question.TYPE_DYNAMIC_CHOICE, "other", "test", "new", "other"),
        # use the new value for single choice if the slug matches the current answer
        (Question.TYPE_DYNAMIC_CHOICE, "test", "test", "new", "new"),
        (Question.TYPE_DYNAMIC_CHOICE, "test", "test", None, None),
        # don't change the value for multi choice if the slug is not present
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, None, "test", "new", None),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["other"], "test", "new", ["other"]),
        # replace the old_slug for multi choice with the new_slug if present
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["test"], "test", "new", ["new"]),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["other", "test"],
            "test",
            "new",
            ["other", "new"],
        ),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["other", "other2"],
            "test",
            "new",
            ["other", "other2"],
        ),
        # discard the old_slug for multi choice if the new_slug is None
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["other", "test"],
            "test",
            None,
            ["other"],
        ),
    ],
)
def test_modify_changed_choice_answer(
    db,
    question_factory,
    answer_factory,
    question_type,
    answer_value,
    old_slug,
    new_slug,
    expected,
):
    """Test the effects of modify_changed_choice_answer.

    For single dynamic choice questions:
    - The old answer value remains unchanged if it doesn't match the old_slug
    - The answer value is replaced with the new_slug if the old_slug matches the old
        answer value
    - The answer value will be None if the new_slug is None

    For multiple dynamic choice questions:
    - The answer list remains unchanged if the old_slug is not in the answer list
    - The old_slug is replaced with the new_slug in the answer list if it is present
    - The old_slug is discarded from the answer list if the new_slug is None
    """
    question = question_factory(type=question_type)
    answer = answer_factory(question=question, value=answer_value)

    assert (
        answer.modify_changed_choice_answer(question, old_slug, new_slug, answer_value)
        == expected
    )
