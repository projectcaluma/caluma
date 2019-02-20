import pytest

from .. import models, serializers
from ...core.tests import extract_serializer_input_fields


@pytest.mark.parametrize(
    "task__type",
    [models.Task.TYPE_SIMPLE, models.Task.TYPE_MULTIPLE_INSTANCE_COMPLETE_TASK_FORM],
)
def test_query_all_tasks(db, snapshot, task, schema_executor):
    query = """
        query AllTasks($name: String!) {
          allTasks(name: $name) {
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

    result = schema_executor(query, variables={"name": task.name})

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
    result = schema_executor(query, variables=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "task__type,operation_name",
    [
        (models.Task.TYPE_SIMPLE, "SaveCompleteTaskFormTask"),
        (
            models.Task.TYPE_MULTIPLE_INSTANCE_COMPLETE_TASK_FORM,
            "SaveMultipleInstanceCompleteTaskFormTask",
        ),
    ],
)
def test_save_complete_task_form_task(
    db, snapshot, task, operation_name, schema_executor
):
    query = """
        fragment TaskProps on Task {
                slug
                name
                __typename
                meta
        }
        mutation SaveCompleteTaskFormTask($input: SaveCompleteTaskFormTaskInput!) {
          saveCompleteTaskFormTask(input: $input) {
            task {
                ...TaskProps
            }
            clientMutationId
          }
        }

        mutation SaveMultipleInstanceCompleteTaskFormTask($input: SaveMultipleInstanceCompleteTaskFormTaskInput!) {
          saveMultipleInstanceCompleteTaskFormTask(input: $input) {
            task {
                ...TaskProps
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
    result = schema_executor(query, variables=inp, operation_name=operation_name)
    assert not result.errors
    snapshot.assert_match(result.data)
