import pytest

from ...caluma_core.tests import extract_serializer_input_fields
from .. import models, serializers


@pytest.mark.parametrize("task__type", [models.Task.TYPE_SIMPLE])
def test_query_all_tasks(db, snapshot, task, schema_executor):
    query = """
        query AllTasks($name: String!) {
          allTasks(filter: [{name: $name}]) {
            totalCount
            edges {
              node {
                __typename
                slug
                name
                description
                meta
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"name": str(task.name)})

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("mutation", ["SaveSimpleTask", "SaveCompleteWorkflowFormTask"])
def test_save_task(db, snapshot, task, mutation, schema_executor):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            task {{
                slug
                name
                __typename
                meta
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(serializers.SaveTaskSerializer, task)
    }
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_comlete_task_form_task(db, snapshot, task, schema_executor):
    query = """
        mutation SaveCompleteTaskFormTask($input: SaveCompleteTaskFormTaskInput!) {
          saveCompleteTaskFormTask(input: $input) {
            task {
                slug
                name
                __typename
                meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveCompleteTaskFormTaskSerializer, task
        )
    }
    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "is_multiple_instance,continue_async,error",
    [
        (True, True, None),
        (True, False, None),
        (False, False, None),
        (False, True, "Only multiple instance tasks can continue asynchronously"),
    ],
)
def test_save_multiple_instance_task(
    db,
    snapshot,
    task,
    schema_executor,
    is_multiple_instance,
    continue_async,
    error,
):
    query = """
        mutation SaveCompleteTaskFormTask($input: SaveSimpleTaskInput!) {
          saveSimpleTask(input: $input) {
            task {
              continueAsync
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "slug": "test",
                "name": "Test",
                "isMultipleInstance": is_multiple_instance,
                "continueAsync": continue_async,
            }
        },
    )

    if error:
        assert error in str(result.errors[0])
    else:
        assert not result.errors
        assert result.data["saveSimpleTask"]["task"]["continueAsync"] == continue_async
