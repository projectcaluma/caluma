import pytest

from .. import models
from ...schema import schema


def test_query_all_tasks(db, snapshot, task):
    query = """
        query AllTasks {
          allTasks {
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema.execute(query)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "task__status,success",
    [(models.Task.STATUS_READY, True), (models.Task.STATUS_COMPLETE, False)],
)
def test_complete_task_last(db, snapshot, task, success):
    query = """
        mutation CompleteTask($input: CompleteTaskInput!) {
          completeTask(input: $input) {
            task {
              status
              workflow {
                status
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": task.pk}}
    result = schema.execute(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize("task__status", [models.Task.STATUS_READY])
def test_complete_task_with_next(db, snapshot, task, flow, task_specification_factory):

    task_specification_next = task_specification_factory()
    flow.next = f"'{task_specification_next.slug}'|taskSpecification"
    flow.save()

    query = """
        mutation CompleteTask($input: CompleteTaskInput!) {
          completeTask(input: $input) {
            task {
              status
              workflow {
                status
                tasks {
                  edges {
                    node {
                      status
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": task.pk}}
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
