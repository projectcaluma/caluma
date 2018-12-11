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
    "work_item__status,case__status,success",
    [
        (models.WorkItem.STATUS_READY, models.Case.STATUS_COMPLETED, True),
        (models.WorkItem.STATUS_COMPLETED, models.Case.STATUS_COMPLETED, False),
        (models.WorkItem.STATUS_READY, models.Case.STATUS_RUNNING, False),
    ],
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


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case", [(models.WorkItem.STATUS_READY, None)]
)
def test_complete_work_item_with_next(
    db,
    snapshot,
    work_item,
    task,
    task_factory,
    task_flow_factory,
    workflow,
    schema_executor,
):

    task_next = task_factory()
    task_flow = task_flow_factory(task=task, workflow=workflow)
    task_flow.flow.next = f"'{task_next.slug}'|task"
    task_flow.flow.save()

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


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case", [(models.WorkItem.STATUS_READY, None)]
)
def test_complete_work_item_with_next_multiple_tasks(
    db,
    snapshot,
    case,
    work_item,
    task,
    task_factory,
    task_flow_factory,
    workflow,
    schema_executor,
):
    task_next_1, task_next_2 = task_factory.create_batch(2)
    task_flow = task_flow_factory(task=task, workflow=workflow)
    task_flow.flow.next = f"['{task_next_1.slug}', '{task_next_2.slug}']|task"
    task_flow.flow.save()

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
    assert case.work_items.count() == 3
    assert set(
        case.work_items.values_list("task", flat=True).filter(
            status=models.WorkItem.STATUS_READY
        )
    ) == {task_next_1.pk, task_next_2.pk}


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case",
    [(models.WorkItem.STATUS_COMPLETED, None)],
)
def test_complete_work_item_with_merge(
    db,
    snapshot,
    case,
    work_item,
    work_item_factory,
    task,
    task_factory,
    flow_factory,
    task_flow_factory,
    workflow,
    schema_executor,
):

    work_item_1, work_item_2 = work_item_factory.create_batch(
        2, status=models.WorkItem.STATUS_READY, child_case=None, case=case
    )
    task_next = task_factory()

    flow = flow_factory(next=f"'{task_next.slug}'|task")
    task_flow_factory(task=work_item_1.task, workflow=workflow, flow=flow)
    task_flow_factory(task=work_item_2.task, workflow=workflow, flow=flow)

    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              id
            }
          }
        }
    """

    inp = {"input": {"id": work_item_1.pk}}
    result = schema_executor(query, variables=inp)

    assert not result.errors
    assert case.work_items.filter(status=models.WorkItem.STATUS_READY).count() == 1
    assert (
        case.work_items.filter(status=models.WorkItem.STATUS_READY).first().pk
        == work_item_2.pk
    )

    inp = {"input": {"id": work_item_2.pk}}
    result = schema_executor(query, variables=inp)
    ready_workitems = case.work_items.filter(status=models.WorkItem.STATUS_READY)
    assert ready_workitems.count() == 1
    assert ready_workitems.first().task == task_next
