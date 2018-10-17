import pytest

from .. import models


def test_query_all_work_items(db, snapshot, work_item, schema_executor):
    query = """
        query WorkItems {
          allWorkItems {
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema_executor(query)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "work_item__status,success",
    [(models.WorkItem.STATUS_READY, True), (models.WorkItem.STATUS_COMPLETE, False)],
)
def test_complete_work_item_last(db, snapshot, work_item, success, schema_executor):
    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              status
              case {
                status
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": work_item.pk}}
    result = schema_executor(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize("work_item__status", [models.WorkItem.STATUS_READY])
def test_complete_work_item_with_next(
    db, snapshot, work_item, flow, task_factory, schema_executor
):

    task_next = task_factory()
    flow.next = f"'{task_next.slug}'|task"
    flow.save()

    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              status
              case {
                status
                workItems {
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

    inp = {"input": {"id": work_item.pk}}
    result = schema_executor(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
