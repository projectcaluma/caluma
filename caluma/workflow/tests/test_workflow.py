import pytest
from graphql_relay import to_global_id

from .. import serializers
from ...core.tests import extract_serializer_input_fields


def test_query_all_workflows(
    db, snapshot, workflow, task_flow, workflow_allow_forms, flow, schema_executor
):
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
                      tasks {
                        slug
                      }
                      next
                    }
                  }
                }
                allowAllForms
                allowForms {
                  edges {
                    node {
                      slug
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variables={"name": workflow.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_workflow(db, snapshot, workflow, workflow_allow_forms, schema_executor):
    query = """
        mutation SaveWorkflow($input: SaveWorkflowInput!) {
          saveWorkflow(input: $input) {
            workflow {
              allowAllForms
              allowForms {
                edges {
                  node {
                    slug
                  }
                }
              }
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
    result = schema_executor(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "task__slug,next",
    [
        ("task-slug", '"task-slug"|task'),
        ("task-slug", '"not-av-task-slug"|task'),
        ("task-slug", '"not-av-task-slug"|invalid'),
        ("task-slug", '""'),
    ],
)
def test_add_workflow_flow(db, workflow, task, snapshot, next, admin_schema_executor):
    query = """
        mutation AddWorkflowFlow($input: AddWorkflowFlowInput!) {
          addWorkflowFlow(input: $input) {
            workflow {
              flows {
                edges {
                  node {
                    createdByUser
                    createdByGroup
                    next
                    tasks {
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

    result = admin_schema_executor(
        query,
        variables={
            "input": {
                "workflow": to_global_id(type(workflow).__name__, workflow.pk),
                "tasks": [to_global_id(type(task).__name__, task.pk)],
                "next": next,
            }
        },
    )
    snapshot.assert_execution_result(result)


def test_remove_flow(db, workflow, task_flow, flow, snapshot, schema_executor):
    query = """
        mutation RemoveFlow($input: RemoveFlowInput!) {
          removeFlow(input: $input) {
            flow {
              next
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(query, variables={"input": {"flow": str(flow.pk)}})
    assert not result.errors
    assert workflow.task_flows.count() == 0
