import pytest
from graphql_relay import to_global_id

from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


def test_query_all_workflow_specifications(db, snapshot, workflow_specification, flow):
    query = """
        query AllWorkflowSpecifications($name: String!) {
          allWorkflowSpecifications(name: $name) {
            edges {
              node {
                slug
                name
                description
                meta
                flows {
                  edges {
                    node {
                      taskSpecification {
                        slug
                      }
                      next
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema.execute(query, variables={"name": workflow_specification.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_workflow_specification(db, snapshot, workflow_specification):
    query = """
        mutation SaveWorkflowSpecification($input: SaveWorkflowSpecificationInput!) {
          saveWorkflowSpecification(input: $input) {
            workflowSpecification {
              slug
              name
              meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveWorkflowSpecificationSerializer, workflow_specification
        )
    }
    workflow_specification.delete()  # test creation
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_publish_workflow_specification(db, workflow_specification, snapshot, flow):
    query = """
        mutation PublishWorkflowSpecification($input: PublishWorkflowSpecificationInput!) {
          publishWorkflowSpecification(input: $input) {
            workflowSpecification {
              isPublished
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={"input": extract_global_id_input_fields(workflow_specification)},
    )

    assert result.data["publishWorkflowSpecification"]["workflowSpecification"][
        "isPublished"
    ]

    workflow_specification.refresh_from_db()
    assert workflow_specification.is_published


def test_archive_workflow_specification(db, workflow_specification):
    query = """
        mutation ArchiveWorkflowSpecification($input: ArchiveWorkflowSpecificationInput!) {
          archiveWorkflowSpecification(input: $input) {
            workflowSpecification {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={"input": extract_global_id_input_fields(workflow_specification)},
    )

    assert not result.errors
    assert result.data["archiveWorkflowSpecification"]["workflowSpecification"][
        "isArchived"
    ]

    workflow_specification.refresh_from_db()
    assert workflow_specification.is_archived


@pytest.mark.parametrize(
    "task_specification__slug,next",
    [
        ("task-slug", '"task-slug"|taskSpecification'),
        ("task-slug", '"not-av-task-slug"|taskSpecification'),
        ("task-slug", '"not-av-task-slug"|invalid'),
        ("task-slug", '""'),
    ],
)
def test_add_workflow_specification_flow(
    db, workflow_specification, task_specification, snapshot, next
):
    query = """
        mutation AddWorkflowSpecificationFlow($input: AddWorkflowSpecificationFlowInput!) {
          addWorkflowSpecificationFlow(input: $input) {
            workflowSpecification {
              flows {
                edges {
                  node {
                    next
                    taskSpecification {
                      slug
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "input": {
                "workflowSpecification": to_global_id(
                    type(workflow_specification).__name__, workflow_specification.pk
                ),
                "taskSpecification": to_global_id(
                    type(task_specification).__name__, task_specification.pk
                ),
                "next": next,
            }
        },
    )
    snapshot.assert_execution_result(result)


def test_remove_workflow_specification_flow(
    db, workflow_specification, task_specification, flow, snapshot
):
    query = """
        mutation RemoveWorkflowSpecificationFlow($input: RemoveWorkflowSpecificationFlowInput!) {
          removeWorkflowSpecificationFlow(input: $input) {
            workflowSpecification {
              flows {
                edges {
                  node {
                    taskSpecification {
                      slug
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "input": {
                "workflowSpecification": to_global_id(
                    type(workflow_specification).__name__, workflow_specification.pk
                ),
                "taskSpecification": to_global_id(
                    type(task_specification).__name__, task_specification.pk
                ),
            }
        },
    )
    assert not result.errors
    assert workflow_specification.flows.count() == 0
