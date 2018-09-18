from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


def test_query_all_task_specifications(db, snapshot, task_specification):
    query = """
        query AllTaskSpecifications($name: String!) {
          allTaskSpecifications(name: $name) {
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

    result = schema.execute(query, variables={"name": task_specification.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_task_specification(db, snapshot, task_specification):
    query = """
        mutation SaveTaskSpecification($input: SaveTaskSpecificationInput!) {
          saveTaskSpecification(input: $input) {
            taskSpecification {
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
        "input": extract_serializer_input_fields(
            serializers.SaveTaskSpecificationSerializer, task_specification
        )
    }
    result = schema.execute(query, variables=inp)
    assert not result.errors
    snapshot.assert_execution_result(result)


def test_archive_task_specification(db, task_specification):
    query = """
        mutation ArchiveTaskSpecification($input: ArchiveTaskSpecificationInput!) {
          archiveTaskSpecification(input: $input) {
            taskSpecification {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(task_specification)}
    )

    assert not result.errors
    assert result.data["archiveTaskSpecification"]["taskSpecification"]["isArchived"]

    task_specification.refresh_from_db()
    assert task_specification.is_archived
