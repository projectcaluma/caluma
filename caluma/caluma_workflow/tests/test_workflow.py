import pytest
from graphql_relay import to_global_id

from ...caluma_core.tests import extract_serializer_input_fields
from .. import serializers


def test_query_all_workflows(
    db,
    snapshot,
    workflow,
    task_flow,
    workflow_start_tasks,
    workflow_allow_forms,
    flow,
    schema_executor,
):
    query = """
        query AllWorkflows($name: String!) {
          allWorkflows(name: $name) {
            totalCount
            edges {
              node {
                slug
                name
                description
                meta
                tasks {
                  slug
                }
                flows {
                  totalCount
                  edges {
                    node {
                      tasks {
                        slug
                      }
                      next
                    }
                  }
                }
                startTasks {
                    slug
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


def test_save_workflow(
    db, snapshot, workflow, workflow_start_tasks, workflow_allow_forms, schema_executor
):
    query = """
        mutation SaveWorkflow($input: SaveWorkflowInput!) {
          saveWorkflow(input: $input) {
            workflow {
              allowAllForms
              allowForms {
                totalCount
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
    "task__slug,next,success",
    [
        ("task-slug", '"task-slug"|task', True),
        ("task-slug", '"not-a-task-slug"|task', False),
        ("task-slug", '"not-a-task-slug"|invalid', False),
        ("task-slug", '""', False),
    ],
)
def test_add_workflow_flow(
    db,
    workflow,
    workflow_start_tasks_factory,
    task,
    snapshot,
    success,
    next,
    admin_schema_executor,
):
    workflow_start_tasks_factory.create_batch(2, workflow=workflow)
    query = """
        mutation AddWorkflowFlow($input: AddWorkflowFlowInput!) {
          addWorkflowFlow(input: $input) {
            workflow {
              tasks {
                slug
              }
              flows {
                totalCount
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
    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


def test_remove_flow(db, workflow, task_flow, flow, schema_executor):
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
