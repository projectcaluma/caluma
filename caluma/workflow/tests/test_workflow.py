import pytest
from graphql_relay import to_global_id

from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


def test_query_all_workflows(db, snapshot, workflow, flow):
    query = """
        query AllWorkflows($name: String!) {
          allWorkflows(name: $name) {
            edges {
              node {
                slug
                name
                description
                meta
                flows {
                  edges {
                    node {
                      task {
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

    result = schema.execute(query, variables={"name": workflow.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_workflow(db, snapshot, workflow):
    query = """
        mutation SaveWorkflow($input: SaveWorkflowInput!) {
          saveWorkflow(input: $input) {
            workflow {
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
            serializers.SaveWorkflowSerializer, workflow
        )
    }
    workflow.delete()  # test creation
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_publish_workflow(db, workflow, snapshot, flow):
    query = """
        mutation PublishWorkflow($input: PublishWorkflowInput!) {
          publishWorkflow(input: $input) {
            workflow {
              isPublished
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(workflow)}
    )

    assert result.data["publishWorkflow"]["workflow"]["isPublished"]

    workflow.refresh_from_db()
    assert workflow.is_published


def test_archive_workflow(db, workflow):
    query = """
        mutation ArchiveWorkflow($input: ArchiveWorkflowInput!) {
          archiveWorkflow(input: $input) {
            workflow {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(workflow)}
    )

    assert not result.errors
    assert result.data["archiveWorkflow"]["workflow"]["isArchived"]

    workflow.refresh_from_db()
    assert workflow.is_archived


@pytest.mark.parametrize(
    "task__slug,next",
    [
        ("task-slug", '"task-slug"|task'),
        ("task-slug", '"not-av-task-slug"|task'),
        ("task-slug", '"not-av-task-slug"|invalid'),
        ("task-slug", '""'),
    ],
)
def test_add_workflow_flow(db, workflow, task, snapshot, next):
    query = """
        mutation AddWorkflowFlow($input: AddWorkflowFlowInput!) {
          addWorkflowFlow(input: $input) {
            workflow {
              flows {
                edges {
                  node {
                    next
                    task {
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
                "workflow": to_global_id(type(workflow).__name__, workflow.pk),
                "task": to_global_id(type(task).__name__, task.pk),
                "next": next,
            }
        },
    )
    snapshot.assert_execution_result(result)


def test_remove_workflow_flow(db, workflow, task, flow, snapshot):
    query = """
        mutation RemoveWorkflowFlow($input: RemoveWorkflowFlowInput!) {
          removeWorkflowFlow(input: $input) {
            workflow {
              flows {
                edges {
                  node {
                    task {
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
                "workflow": to_global_id(type(workflow).__name__, workflow.pk),
                "task": to_global_id(type(task).__name__, task.pk),
            }
        },
    )
    assert not result.errors
    assert workflow.flows.count() == 0
