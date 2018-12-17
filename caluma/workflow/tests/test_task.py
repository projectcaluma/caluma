import pytest

from .. import serializers
from ...core.tests import (
    extract_global_id_input_fields,
    extract_serializer_input_fields,
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
    snapshot.assert_execution_result(result)


def test_archive_task(db, task, schema_executor):
    query = """
        mutation ArchiveTask($input: ArchiveTaskInput!) {
          archiveTask(input: $input) {
            task {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variables={"input": extract_global_id_input_fields(task)}
    )

    assert not result.errors
    assert result.data["archiveTask"]["task"]["isArchived"]

    task.refresh_from_db()
    assert task.is_archived
