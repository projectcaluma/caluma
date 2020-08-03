import pytest
from graphql_relay import to_global_id

from caluma.caluma_core.tests import extract_serializer_input_fields

from .. import models, serializers


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

    result = schema_executor(query, variable_values={"name": workflow.name})

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
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "task__slug,next,success",
    [
        ("task-slug", '"task-slug"|task', True),
        ("task-slug", '"not-a-task-slug"|task', False),
        ("task-slug", '["not-a-task-slug"]|tasks', False),
        ("task-slug", '"not-a-task-slug"|invalid', False),
        ("task-slug", '""', False),
    ],
)
def test_add_workflow_flow(
    db,
    workflow,
    workflow_start_tasks_factory,
    task,
    sorted_snapshot,
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
        variable_values={
            "input": {
                "workflow": to_global_id(type(workflow).__name__, workflow.pk),
                "tasks": [to_global_id(type(task).__name__, task.pk)],
                "next": next,
            }
        },
    )
    assert not bool(result.errors) == success
    if success:
        assert result.data == sorted_snapshot("tasks", lambda el: el["slug"])


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

    result = schema_executor(query, variable_values={"input": {"flow": str(flow.pk)}})
    assert not result.errors
    assert workflow.task_flows.count() == 0


def test_add_workflow_flow_reuse_task(
    db, workflow_start_tasks_factory, task_factory, snapshot, admin_schema_executor
):
    """Test that the same tasks can be reused in multiple flows."""

    task_a, task_b = task_factory.create_batch(2, type=models.Task.TYPE_SIMPLE)
    workflow_a = workflow_start_tasks_factory(
        task=task_a, workflow__slug="workflow-a"
    ).workflow
    workflow_b = workflow_start_tasks_factory(
        task=task_b, workflow__slug="workflow-b"
    ).workflow

    query = """
    mutation AddWorkflowFlow($input: AddWorkflowFlowInput!) {
      addWorkflowFlow(input: $input) {
        clientMutationId
      }
    }
    """

    result = admin_schema_executor(
        query,
        variable_values={
            "input": {
                "workflow": workflow_a.slug,
                "tasks": [task_a.slug],
                "next": f"'{task_b.slug}'|task",
            }
        },
    )
    assert not result.errors

    result = admin_schema_executor(
        query,
        variable_values={
            "input": {
                "workflow": workflow_b.slug,
                "tasks": [task_a.slug],
                "next": f"'{task_b.slug}'|task",
            }
        },
    )
    assert not result.errors

    task_flows = models.TaskFlow.objects.all()
    assert task_flows.count() == 2
    assert (
        task_flows.get(workflow=workflow_a).flow
        != task_flows.get(workflow=workflow_b).flow
    )
    assert (
        task_flows.get(workflow=workflow_a).flow.next
        == task_flows.get(workflow=workflow_b).flow.next
    )
