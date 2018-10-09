from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


def test_query_all_tasks(db, snapshot, task):
    query = """
        query AllTasks($name: String!) {
          allTasks(name: $name) {
            edges {
              node {
                type
                slug
                name
                description
                meta
              }
            }
          }
        }
    """

    result = schema.execute(query, variables={"name": task.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_task(db, snapshot, task):
    query = """
        mutation SaveTask($input: SaveTaskInput!) {
          saveTask(input: $input) {
            task {
                slug
                name
                type
                meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(serializers.SaveTaskSerializer, task)
    }
    result = schema.execute(query, variables=inp)
    assert not result.errors
    snapshot.assert_execution_result(result)


def test_archive_task(db, task):
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

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(task)}
    )

    assert not result.errors
    assert result.data["archiveTask"]["task"]["isArchived"]

    task.refresh_from_db()
    assert task.is_archived
