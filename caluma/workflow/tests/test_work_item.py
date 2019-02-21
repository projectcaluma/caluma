import json

import pytest
from graphene.utils.str_converters import to_const

from .. import models
from ...core.relay import extract_global_id
from ...form.models import Question


def test_query_all_work_items_filter_status(db, work_item_factory, schema_executor):
    work_item_factory(status=models.WorkItem.STATUS_READY)
    work_item_factory(status=models.WorkItem.STATUS_COMPLETED)

    query = """
        query WorkItems($status: WorkItemStatusArgument!) {
          allWorkItems(status: $status) {
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema_executor(
        query, variables={"status": to_const(models.WorkItem.STATUS_READY)}
    )

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 1
    assert result.data["allWorkItems"]["edges"][0]["node"]["status"] == to_const(
        models.WorkItem.STATUS_READY
    )


@pytest.mark.parametrize("task__type,task__form", [(models.Task.TYPE_SIMPLE, None)])
@pytest.mark.parametrize(
    "work_item__status,case__status,success",
    [
        (models.WorkItem.STATUS_READY, models.Case.STATUS_COMPLETED, True),
        (models.WorkItem.STATUS_COMPLETED, models.Case.STATUS_COMPLETED, False),
        (models.WorkItem.STATUS_READY, models.Case.STATUS_RUNNING, False),
    ],
)
def test_complete_work_item_last(
    db, snapshot, work_item, success, admin_schema_executor
):
    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              closedByUser
              status
              case {
                closedByUser
                status

              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": work_item.pk}}
    result = admin_schema_executor(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,case__status,task__type,question__type,answer__value,success",
    [
        (
            models.WorkItem.STATUS_READY,
            None,
            models.Case.STATUS_RUNNING,
            models.Task.TYPE_COMPLETE_WORKFLOW_FORM,
            Question.TYPE_FLOAT,
            1.0,
            True,
        ),
        (
            models.WorkItem.STATUS_READY,
            None,
            models.Case.STATUS_RUNNING,
            models.Task.TYPE_COMPLETE_WORKFLOW_FORM,
            Question.TYPE_TEXT,
            "",
            False,
        ),
    ],
)
def test_complete_workflow_form_work_item(
    db,
    work_item,
    answer,
    question_factory,
    answer_factory,
    answer_document_factory,
    form_question,
    success,
    schema_executor,
):
    table_question = question_factory(type=Question.TYPE_TABLE)
    table_answer = answer_factory(
        question=table_question, document=answer.document, value=None
    )
    answer_document = answer_document_factory(answer=table_answer)
    answer_document.document.answers.add(answer_factory())

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
        assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
            models.WorkItem.STATUS_COMPLETED
        )
        assert result.data["completeWorkItem"]["workItem"]["case"][
            "status"
        ] == to_const(models.Case.STATUS_COMPLETED)


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,case__status,task__type,case__document",
    [
        (
            models.WorkItem.STATUS_READY,
            None,
            models.Case.STATUS_RUNNING,
            models.Task.TYPE_COMPLETE_TASK_FORM,
            None,
        )
    ],
)
@pytest.mark.parametrize(
    "question__type,answer__value,success",
    [(Question.TYPE_INTEGER, 1, True), (Question.TYPE_CHOICE, "", False)],
)
def test_complete_task_form_work_item(
    db, work_item, answer, form_question, success, schema_executor
):
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
        assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
            models.WorkItem.STATUS_COMPLETED
        )
        assert result.data["completeWorkItem"]["workItem"]["case"][
            "status"
        ] == to_const(models.Case.STATUS_COMPLETED)


@pytest.mark.parametrize("question__type,answer__value", [(Question.TYPE_INTEGER, 1)])
def test_complete_multiple_instance_task_form_work_item(
    db, task_factory, work_item_factory, answer, form_question, schema_executor
):
    task = task_factory(is_multiple_instance=True)
    work_item_1 = work_item_factory(task=task, child_case=None)
    work_item_2 = work_item_factory(task=task, child_case=None, case=work_item_1.case)
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

    inp = {"input": {"id": work_item_1.pk}}
    result = schema_executor(query, variables=inp)

    assert not bool(result.errors)
    assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
        models.WorkItem.STATUS_COMPLETED
    )
    assert result.data["completeWorkItem"]["workItem"]["case"]["status"] == to_const(
        models.Case.STATUS_RUNNING
    )

    inp = {"input": {"id": work_item_2.pk}}
    result = schema_executor(query, variables=inp)

    assert not bool(result.errors)
    assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
        models.WorkItem.STATUS_COMPLETED
    )
    assert result.data["completeWorkItem"]["workItem"]["case"]["status"] == to_const(
        models.Case.STATUS_COMPLETED
    )


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,task__type",
    [(models.WorkItem.STATUS_READY, None, models.Task.TYPE_SIMPLE)],
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

    task_next = task_factory(
        type=models.Task.TYPE_SIMPLE, form=None, address_groups='["group-name"]|groups'
    )
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
                workItems(orderBy: STATUS_DESC) {
                  edges {
                    node {
                      status
                      addressedGroups
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
    "work_item__status,work_item__child_case,task__type",
    [(models.WorkItem.STATUS_READY, None, models.Task.TYPE_SIMPLE)],
)
def test_complete_work_item_with_next_multiple_tasks(
    db,
    case,
    work_item,
    task,
    task_factory,
    task_flow_factory,
    workflow,
    schema_executor,
):
    task_next_1, task_next_2 = task_factory.create_batch(
        2, type=models.Task.TYPE_SIMPLE
    )
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
    "work_item__status,work_item__child_case,task__type",
    [(models.WorkItem.STATUS_READY, None, models.Task.TYPE_SIMPLE)],
)
def test_complete_work_item_with_next_multiple_instance_task(
    db,
    case,
    work_item,
    task,
    task_factory,
    task_flow_factory,
    workflow,
    schema_executor,
):
    task_next = task_factory.create(
        is_multiple_instance=True, address_groups=["group1", "group2", "group3"]
    )
    task_flow = task_flow_factory(task=task, workflow=workflow)
    task_flow.flow.next = f"['{task_next.slug}']|task"
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
    assert case.work_items.filter(status=models.WorkItem.STATUS_READY).count() == 3
    assert case.work_items.filter(status=models.WorkItem.STATUS_COMPLETED).count() == 1
    for work_item in case.work_items.filter(status=models.WorkItem.STATUS_READY):
        assert len(work_item.addressed_groups) == 1


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,task__type",
    [(models.WorkItem.STATUS_COMPLETED, None, models.Task.TYPE_SIMPLE)],
)
def test_complete_work_item_with_merge(
    db,
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
    # create two work items which can be processed in parallel
    task_1, task_2 = task_factory.create_batch(2, type=models.Task.TYPE_SIMPLE)
    work_item_1 = work_item_factory(
        task=task_1, status=models.WorkItem.STATUS_READY, child_case=None, case=case
    )
    work_item_2 = work_item_factory(
        task=task_2, status=models.WorkItem.STATUS_READY, child_case=None, case=case
    )
    ready_workitems = case.work_items.filter(status=models.WorkItem.STATUS_READY)
    assert ready_workitems.count() == 2

    # both work item's tasks reference the same merge task
    task_merge = task_factory(type=models.Task.TYPE_COMPLETE_TASK_FORM)
    flow = flow_factory(next=f"'{task_merge.slug}'|task")
    task_flow_factory(task=work_item_1.task, workflow=workflow, flow=flow)
    task_flow_factory(task=work_item_2.task, workflow=workflow, flow=flow)

    # complete one of the work item
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

    # one parallel work item is left, no new one created as both preceding
    # work items need to be completed first
    assert ready_workitems.count() == 1
    assert ready_workitems.first().pk == work_item_2.pk

    # complete second work item
    inp = {"input": {"id": work_item_2.pk}}
    result = schema_executor(query, variables=inp)
    assert not result.errors

    # new work item is created of merge task
    assert ready_workitems.count() == 1
    ready_workitem = ready_workitems.first()
    assert ready_workitem.task == task_merge
    assert ready_workitem.document_id is not None


def test_save_work_item(db, work_item, schema_executor):
    query = """
        mutation SaveWorkItem($input: SaveWorkItemInput!) {
          saveWorkItem(input: $input) {
            clientMutationId
          }
        }
    """

    assigned_users = ["user1", "user2"]
    inp = {
        "input": {
            "workItem": str(work_item.pk),
            "assignedUsers": assigned_users,
            "meta": json.dumps({"test": "test"}),
        }
    }
    result = schema_executor(query, variables=inp)

    assert not result.errors
    work_item.refresh_from_db()
    assert work_item.assigned_users == assigned_users
    assert work_item.meta == {"test": "test"}


@pytest.mark.parametrize(
    "task__is_multiple_instance,work_item__status,work_item__child_case, success",
    [
        (False, models.WorkItem.STATUS_READY, None, False),
        (True, models.WorkItem.STATUS_COMPLETED, None, False),
        (True, models.WorkItem.STATUS_READY, None, True),
    ],
)
def test_create_work_item(db, work_item, success, schema_executor):
    query = """
        mutation CreateWorkItem($input: CreateWorkItemInput!) {
          createWorkItem(input: $input) {
            clientMutationId
            workItem {
                id
            }
          }
        }
    """
    assigned_users = ["user1", "user2"]
    meta = {"test": "test"}
    inp = {
        "input": {
            "case": str(work_item.case.pk),
            "multipleInstanceTask": str(work_item.task.pk),
            "assignedUsers": assigned_users,
            "meta": json.dumps(meta),
        }
    }
    result = schema_executor(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        pk = extract_global_id(result.data["createWorkItem"]["workItem"]["id"])
        new_work_item = models.WorkItem.objects.get(pk=pk)
        assert new_work_item.assigned_users == assigned_users
        assert new_work_item.status == models.WorkItem.STATUS_READY
        assert new_work_item.meta == meta
