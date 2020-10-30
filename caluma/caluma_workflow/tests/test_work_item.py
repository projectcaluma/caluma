import json

import pytest
from django.core.exceptions import ValidationError
from graphene.utils.str_converters import to_const

from ...caluma_core.relay import extract_global_id
from ...caluma_form.models import Question
from ...caluma_user.models import BaseUser
from .. import api, models


def test_query_all_work_items_filter_status(db, work_item_factory, schema_executor):
    work_item_factory(status=models.WorkItem.STATUS_READY)
    work_item_factory(status=models.WorkItem.STATUS_COMPLETED)

    query = """
        query WorkItems($status: WorkItemStatusArgument!) {
          allWorkItems(status: $status) {
            totalCount
            edges {
              node {
                status
              }
            }
          }
        }
    """

    result = schema_executor(
        query, variable_values={"status": to_const(models.WorkItem.STATUS_READY)}
    )

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 1
    assert result.data["allWorkItems"]["edges"][0]["node"]["status"] == to_const(
        models.WorkItem.STATUS_READY
    )


@pytest.mark.parametrize("key", ["addressed_groups", "controlling_groups"])
def test_query_all_work_items_filter_groups(
    db, key, work_item_factory, schema_executor
):
    factory_kwargs = {key: ["A", "B"]}
    work_item_factory(**factory_kwargs)

    query = """
        query WorkItems($groups: [String]!) {
          allWorkItems(addressedGroups: $groups) {
            edges {
              node {
                addressedGroups
              }
            }
          }
        }
    """

    if key == "controlling_groups":
        query = """
            query WorkItems($groups: [String]!) {
              allWorkItems(controllingGroups: $groups) {
                edges {
                  node {
                    controllingGroups
                  }
                }
              }
            }
        """

    result = schema_executor(query, variable_values={"groups": ["B", "C"]})

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 1
    assert result.data["allWorkItems"]["edges"][0]["node"][key.replace("_g", "G")] == [
        "A",
        "B",
    ]

    result = schema_executor(query, variable_values={"groups": ["C", "D"]})

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == 0


@pytest.mark.parametrize("task__type,task__form", [(models.Task.TYPE_SIMPLE, None)])
@pytest.mark.parametrize(
    "work_item__status,case__status,child_case_status,error",
    [
        (models.WorkItem.STATUS_READY, models.Case.STATUS_RUNNING, None, None),
        (
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
            models.Case.STATUS_COMPLETED,
            None,
        ),
        (
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
            models.Case.STATUS_COMPLETED,
            None,
        ),
        (
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_COMPLETED,
            None,
            "Only work items of running cases can be completed.",
        ),
        (
            models.WorkItem.STATUS_COMPLETED,
            models.Case.STATUS_RUNNING,
            None,
            "Only ready work items can be completed.",
        ),
        (
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
            models.Case.STATUS_RUNNING,
            "Work item can only be completed when child case is in a finish state.",
        ),
    ],
)
def test_complete_work_item_last(
    db,
    snapshot,
    work_item,
    case_factory,
    child_case_status,
    error,
    admin_schema_executor,
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
    work_item.child_case = child_case_status and case_factory(status=child_case_status)
    work_item.save()

    inp = {"input": {"id": work_item.pk}}
    result = admin_schema_executor(query, variable_values=inp)

    assert bool(result.errors) == bool(error)
    if error:
        assert error in str(result.errors[0])
    else:
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
    result = schema_executor(query, variable_values=inp)

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
    result = schema_executor(query, variable_values=inp)

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
    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors)
    assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
        models.WorkItem.STATUS_COMPLETED
    )
    assert result.data["completeWorkItem"]["workItem"]["case"]["status"] == to_const(
        models.Case.STATUS_RUNNING
    )

    inp = {"input": {"id": work_item_2.pk}}
    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors)
    assert result.data["completeWorkItem"]["workItem"]["status"] == to_const(
        models.WorkItem.STATUS_COMPLETED
    )
    assert result.data["completeWorkItem"]["workItem"]["case"]["status"] == to_const(
        models.Case.STATUS_COMPLETED
    )


@pytest.mark.parametrize("question__type,answer__value", [(Question.TYPE_INTEGER, 1)])
def test_complete_multiple_instance_task_form_work_item_next(
    db,
    task_factory,
    task_flow_factory,
    work_item_factory,
    answer,
    form_question,
    snapshot,
    schema_executor,
):
    task = task_factory(is_multiple_instance=True)
    work_item = work_item_factory(task=task, child_case=None)
    work_item_factory(
        task=task,
        child_case=None,
        status=models.WorkItem.STATUS_COMPLETED,
        case=work_item.case,
    )

    task_next = task_factory(
        type=models.Task.TYPE_SIMPLE, form=None, address_groups='["group-name"]|groups'
    )
    task_flow = task_flow_factory(task=task, workflow=work_item.case.workflow)
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
                  totalCount
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
    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors)
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,task__type,work_item__controlling_groups,work_item__created_by_group,case__created_by_group",
    [
        (
            models.WorkItem.STATUS_READY,
            None,
            models.Task.TYPE_SIMPLE,
            ["controlling-group1", "controlling-group2"],
            "work-item-creating-group",
            "case-creating-group",
        )
    ],
)
@pytest.mark.parametrize(
    "group_jexl,is_multiple_instance",
    [
        ('["some-group"]|groups', False),
        ("info.prev_work_item.controlling_groups", False),
        ("info.work_item.created_by_group", False),
        ("info.case.created_by_group", False),
        ("[info.case.created_by_group, info.work_item.created_by_group]|groups", False),
        ("[info.case.created_by_group, info.work_item.created_by_group]", False),
        ("[info.case.created_by_group, info.work_item.created_by_group]", True),
        ("[]", False),
        ("[]", True),
    ],
)
def test_complete_work_item_with_next(
    db,
    group_jexl,
    is_multiple_instance,
    sorted_snapshot,
    work_item,
    task,
    task_factory,
    task_flow_factory,
    workflow,
    info,
    case,
    schema_executor,
):
    class FakeUser(BaseUser):
        def __init__(self):
            self.username = "foo"
            self.groups = ["fake-user-group"]

        @property
        def group(self):
            return self.groups[0]

    info.context.user = FakeUser()

    task_next = task_factory(
        type=models.Task.TYPE_SIMPLE,
        form=None,
        address_groups=group_jexl,
        control_groups=group_jexl,
        is_multiple_instance=is_multiple_instance,
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
                  totalCount
                  edges {
                    node {
                      status
                      addressedGroups
                      controllingGroups
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
    result = schema_executor(query, variable_values=inp, info=info)

    assert not result.errors
    assert result.data == sorted_snapshot("edges", lambda x: json.dumps(x))


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
    task_flow.flow.next = f"['{task_next_1.slug}', '{task_next_2.slug}']|tasks"
    task_flow.flow.save()

    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              status
              case {
                status
                workItems {
                  totalCount
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
    result = schema_executor(query, variable_values=inp)

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
    task_flow.flow.next = f"['{task_next.slug}']|tasks"
    task_flow.flow.save()

    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            workItem {
              status
              case {
                status
                workItems {
                  totalCount
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
    result = schema_executor(query, variable_values=inp)

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
    result = schema_executor(query, variable_values=inp)
    assert not result.errors

    # one parallel work item is left, no new one created as both preceding
    # work items need to be completed first
    assert ready_workitems.count() == 1
    assert ready_workitems.first().pk == work_item_2.pk

    # complete second work item
    inp = {"input": {"id": work_item_2.pk}}
    result = schema_executor(query, variable_values=inp)
    assert not result.errors

    # new work item is created of merge task
    assert ready_workitems.count() == 1
    ready_workitem = ready_workitems.first()
    assert ready_workitem.task == task_merge
    assert ready_workitem.document_id is not None


@pytest.mark.parametrize(
    "work_item_name,work_item_description,expected_name,expected_description",
    [
        (None, None, "Task name", "Task description"),
        (
            "WorkItem name",
            "WorkItem description",
            "WorkItem name",
            "WorkItem description",
        ),
    ],
)
@pytest.mark.parametrize(
    "task__name,task__description", [("Task name", "Task description")]
)
def test_save_work_item(
    db,
    work_item,
    work_item_name,
    work_item_description,
    expected_name,
    expected_description,
    schema_executor,
):
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
            "name": work_item_name,
            "description": work_item_description,
        }
    }
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    work_item.refresh_from_db()
    assert work_item.assigned_users == assigned_users
    assert work_item.meta == {"test": "test"}
    assert work_item.name.en == expected_name
    assert work_item.description.en == expected_description


@pytest.mark.parametrize(
    "task__is_multiple_instance,task__control_groups,expected_groups,work_item__status,set_groups,success",
    [
        # Failing
        (False, None, None, models.WorkItem.STATUS_READY, False, False),
        (True, None, None, models.WorkItem.STATUS_COMPLETED, False, False),
        # Successful
        (
            True,
            '["groups-transform"]|groups',
            ["groups-transform"],
            models.WorkItem.STATUS_READY,
            False,
            True,
        ),
        (
            True,
            "info.case.created_by_group",
            ["group-case"],
            models.WorkItem.STATUS_READY,
            False,
            True,
        ),
        (
            True,
            "info.work_item.created_by_group",
            ["group-work-item"],
            models.WorkItem.STATUS_READY,
            False,
            True,
        ),
        # Controlling jexl evaluates to None
        (True, "", [], models.WorkItem.STATUS_READY, False, True),
        (True, None, [], models.WorkItem.STATUS_READY, False, True),
        (
            True,
            "info.prev_work_item.controlling_groups",
            [],
            models.WorkItem.STATUS_READY,
            False,
            True,
        ),
        # Reset controlling_groups and addressed_groups
        (
            True,
            "info.work_item.created_by_group",
            [],
            models.WorkItem.STATUS_READY,
            True,
            True,
        ),
    ],
)
@pytest.mark.parametrize("case__created_by_group", ["group-case"])
@pytest.mark.parametrize("work_item__child_case", [None])
@pytest.mark.parametrize(
    "task__name,task__description", [("Task name", "Task description")]
)
def test_create_work_item(
    db, work_item, task, expected_groups, set_groups, success, schema_executor, info
):
    task.address_groups = task.control_groups
    task.save()

    class FakeUser(BaseUser):
        def __init__(self):
            self.username = "foo"
            self.groups = ["group-work-item"]

        @property
        def group(self):
            return self.groups[0]

    info.context.user = FakeUser()

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
            "description": "work_item description",
        }
    }

    if set_groups:
        inp["input"]["controllingGroups"] = []
        inp["input"]["addressedGroups"] = []

    result = schema_executor(query, variable_values=inp, info=info)

    assert not bool(result.errors) == success
    if success:
        pk = extract_global_id(result.data["createWorkItem"]["workItem"]["id"])
        new_work_item = models.WorkItem.objects.get(pk=pk)
        assert new_work_item.assigned_users == assigned_users
        assert new_work_item.status == models.WorkItem.STATUS_READY
        assert new_work_item.meta == meta
        assert new_work_item.document is not None
        assert new_work_item.controlling_groups == expected_groups
        assert new_work_item.addressed_groups == expected_groups
        assert dict(new_work_item.name) == {"en": "Task name", "de": None, "fr": None}
        assert dict(new_work_item.description) == {
            "en": "work_item description",
            "de": None,
            "fr": None,
        }


def test_filter_document_has_answer(
    db, schema_executor, simple_case, work_item_factory
):
    item_a, item_b = work_item_factory.create_batch(2)

    item_a.document = simple_case.document
    item_a.save()
    item_b.case = simple_case
    item_b.save()

    answer = simple_case.document.answers.first()
    answer.value = "foo"
    answer.save()
    answer.question.type = answer.question.TYPE_TEXT
    answer.question.save()

    query_expect = [("documentHasAnswer", item_a), ("caseDocumentHasAnswer", item_b)]

    for filt, expected in query_expect:
        query = """
            query WorkItems($has_answer: [HasAnswerFilterType!]) {
              allWorkItems(%(filt)s: $has_answer) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        """ % {
            "filt": filt
        }

        result = schema_executor(
            query,
            variable_values={
                "has_answer": [{"question": answer.question_id, "value": "foo"}]
            },
        )

        assert not result.errors
        assert len(result.data["allWorkItems"]["edges"]) == 1
        node_id = extract_global_id(
            result.data["allWorkItems"]["edges"][0]["node"]["id"]
        )
        assert node_id == str(expected.id)


@pytest.mark.parametrize(
    "lookup_expr,int,value,len_results",
    [
        (None, False, "value1", 1),
        ("EXACT", False, "value1", 1),
        ("EXACT", False, "value", 0),
        ("STARTSWITH", False, "alue1", 0),
        ("STARTSWITH", False, "val", 2),
        ("CONTAINS", False, "alue", 2),
        ("CONTAINS", False, "AlUe", 0),
        ("ICONTAINS", False, "AlUe", 2),
        ("GTE", True, 2, 2),
        ("GTE", True, 5, 1),
        ("GTE", True, 6, 0),
        ("GT", True, 4, 1),
        ("GT", True, 5, 0),
        ("LTE", True, 1, 0),
        ("LTE", True, 2, 1),
        ("LTE", True, 6, 2),
        ("LT", True, 2, 0),
        ("LT", True, 6, 2),
    ],
)
def test_query_all_work_items_filter_case_meta_value(
    db, work_item_factory, schema_executor, lookup_expr, int, value, len_results
):
    work_item_factory(case__meta={"testkey": 2 if int else "value1"})
    work_item_factory(case__meta={"testkey": 5 if int else "value2"})
    work_item_factory(case__meta={"testkey2": 2 if int else "value1"})

    query = """
        query WorkItems($case_meta_value: [JSONValueFilterType!]) {
          allWorkItems(caseMetaValue: $case_meta_value) {
            totalCount
            edges {
              node {
                case {
                  meta
                }
              }
            }
          }
        }
    """

    variables = {"key": "testkey", "value": value}

    if lookup_expr:
        variables["lookup"] = lookup_expr

    result = schema_executor(query, variable_values={"case_meta_value": [variables]})

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == len_results


@pytest.mark.parametrize("value,len_results", [(1, 3), (2, 0), (3, 0), (4, 1)])
def test_query_all_work_items_filter_root_case_meta_value(
    db, work_item_factory, case_factory, schema_executor, value, len_results
):
    case = case_factory(meta={"testkey": 1})
    child_case = case_factory(meta={"testkey": 2}, family=case)
    child_child_case = case_factory(meta={"testkey": 3}, family=case)
    unrelated_case = case_factory(meta={"testkey": 4})

    # create a tree of case - work_item - child_case - workitem - child_child_case - work_item
    work_item_factory(case=case, child_case=child_case)
    work_item_factory(case=child_case, child_case=child_child_case)
    work_item_factory(case=child_child_case)
    work_item_factory(case=unrelated_case)

    query = """
        query WorkItems($root_case_meta_value: [JSONValueFilterType!]) {
          allWorkItems(rootCaseMetaValue: $root_case_meta_value) {
            totalCount
            edges {
              node {
                case {
                  meta
                }
              }
            }
          }
        }
    """

    variables = {"key": "testkey", "value": value}

    result = schema_executor(
        query, variable_values={"root_case_meta_value": [variables]}
    )

    assert not result.errors
    assert len(result.data["allWorkItems"]["edges"]) == len_results


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
    "question__type,answer__value",
    [(Question.TYPE_INTEGER, 1), (Question.TYPE_CHOICE, "")],
)
def test_skip_task_form_work_item(
    db, work_item, answer, form_question, schema_executor
):
    query = """
        mutation SkipWorkItem($input: SkipWorkItemInput!) {
          skipWorkItem(input: $input) {
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
    result = schema_executor(query, variable_values=inp)

    # when skipping, both valid and invalid forms don't matter (contrary
    # to completion, where it DOES matter)
    assert not bool(result.errors)
    assert result.data["skipWorkItem"]["workItem"]["status"] == to_const(
        models.WorkItem.STATUS_SKIPPED
    )
    assert result.data["skipWorkItem"]["workItem"]["case"]["status"] == to_const(
        models.Case.STATUS_COMPLETED
    )


@pytest.mark.parametrize(
    "work_item_status,case__status,error",
    [
        (
            models.WorkItem.STATUS_COMPLETED,
            models.Case.STATUS_RUNNING,
            "Only ready work items can be skipped.",
        ),
        (
            models.WorkItem.STATUS_CANCELED,
            models.Case.STATUS_RUNNING,
            "Only ready work items can be skipped.",
        ),
        (
            models.WorkItem.STATUS_SKIPPED,
            models.Case.STATUS_RUNNING,
            "Only ready work items can be skipped.",
        ),
        (
            models.WorkItem.STATUS_SUSPENDED,
            models.Case.STATUS_RUNNING,
            "Only ready work items can be skipped.",
        ),
        (
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_COMPLETED,
            "Only work items of running cases can be skipped.",
        ),
        (models.WorkItem.STATUS_READY, models.Case.STATUS_RUNNING, None),
    ],
)
@pytest.mark.parametrize("question__type,answer__value", [(Question.TYPE_INTEGER, 1)])
def test_skip_multiple_instance_task_form_work_item(
    db,
    task_factory,
    work_item_factory,
    case,
    answer,
    form_question,
    work_item_status,
    error,
    schema_executor,
):
    task = task_factory(is_multiple_instance=True)
    work_item_1 = work_item_factory(
        task=task, case=case, child_case=None, status=work_item_status
    )
    work_item_2 = work_item_factory(task=task, case=case, child_case=None)
    query = """
        mutation SkipWorkItem($input: SkipWorkItemInput!) {
          skipWorkItem(input: $input) {
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
    result = schema_executor(query, variable_values=inp)

    assert bool(result.errors) == bool(error)

    if error:
        assert error in str(result.errors[0])

    else:

        assert result.data["skipWorkItem"]["workItem"]["status"] == to_const(
            models.WorkItem.STATUS_SKIPPED
        )
        assert result.data["skipWorkItem"]["workItem"]["case"]["status"] == to_const(
            models.Case.STATUS_RUNNING
        )

        inp = {"input": {"id": work_item_2.pk}}
        result = schema_executor(query, variable_values=inp)

        assert not bool(result.errors)
        assert result.data["skipWorkItem"]["workItem"]["status"] == to_const(
            models.WorkItem.STATUS_SKIPPED
        )
        assert result.data["skipWorkItem"]["workItem"]["case"]["status"] == to_const(
            models.Case.STATUS_COMPLETED
        )


@pytest.mark.parametrize("task__type,task__form", [(models.Task.TYPE_SIMPLE, None)])
@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,case__status",
    [(models.WorkItem.STATUS_READY, None, models.Case.STATUS_RUNNING)],
)
def test_complete_work_item_last_api(db, work_item, admin_user):
    api.complete_work_item(work_item, admin_user)

    work_item.refresh_from_db()

    assert work_item.status == models.WorkItem.STATUS_COMPLETED
    assert work_item.case.status == models.Case.STATUS_COMPLETED


@pytest.mark.parametrize("task__type,task__form", [(models.Task.TYPE_SIMPLE, None)])
@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,case__status",
    [(models.WorkItem.STATUS_READY, None, models.Case.STATUS_RUNNING)],
)
def test_skip_work_item_last_api(db, work_item, admin_user):
    api.skip_work_item(work_item, admin_user)

    work_item.refresh_from_db()

    assert work_item.status == models.WorkItem.STATUS_SKIPPED
    assert work_item.case.status == models.Case.STATUS_COMPLETED


@pytest.mark.parametrize("task__type,task__form", [(models.Task.TYPE_SIMPLE, None)])
@pytest.mark.parametrize(
    "work_item__status,case__status",
    [(models.WorkItem.STATUS_READY, models.Case.STATUS_RUNNING)],
)
def test_skip_work_item_child_case(db, work_item, case_factory, admin_user):
    work_item.child_case = case_factory()

    assert work_item.child_case.status == models.Case.STATUS_RUNNING

    api.skip_work_item(work_item, admin_user)

    work_item.refresh_from_db()

    assert work_item.child_case.status == models.Case.STATUS_CANCELED


@pytest.mark.parametrize(
    "work_item__status,work_item__child_case,task__type",
    [(models.WorkItem.STATUS_COMPLETED, None, models.Task.TYPE_SIMPLE)],
)
def test_complete_work_item_parallel(
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
    admin_user,
):
    # create two work items which can be processed in parallel
    task_1, task_2 = task_factory.create_batch(2, type=models.Task.TYPE_SIMPLE)
    flow = flow_factory(next=f"['{task_1.slug}','{task_2.slug}']|tasks")
    task_flow_factory(task=work_item.task, workflow=workflow, flow=flow)
    work_item_factory(
        task=task_1, status=models.WorkItem.STATUS_READY, child_case=None, case=case
    )
    work_item_factory(
        task=task_2, status=models.WorkItem.STATUS_READY, child_case=None, case=case
    )

    ready_work_items = case.work_items.filter(status=models.WorkItem.STATUS_READY)

    for i, ready_work_item in enumerate(ready_work_items):
        api.complete_work_item(ready_work_item, admin_user)

        ready_work_item.refresh_from_db()
        case.refresh_from_db()

        assert ready_work_item.status == models.WorkItem.STATUS_COMPLETED

        # if we have multiple parallel running work items without a flow (end
        # of the workflow), the case should only be completed when all parallel
        # work items are completed
        if i + 1 == len(ready_work_items):
            assert case.status == models.Case.STATUS_COMPLETED
        else:
            assert case.status == models.Case.STATUS_RUNNING


def test_complete_work_item_same_task_multiple_workflows(
    db,
    case_factory,
    work_item_factory,
    task_factory,
    flow_factory,
    task_flow_factory,
    workflow_factory,
    schema_executor,
    admin_user,
):
    workflow_1, workflow_2 = workflow_factory.create_batch(2)
    # create two work items which can be processed in parallel
    task_1, task_2 = task_factory.create_batch(2, type=models.Task.TYPE_SIMPLE)

    flow = flow_factory(next=f"'{task_2.slug}'|task")

    # workflow 1 consists out of 2 tasks, workflow_2 just out of one
    task_flow_factory(task=task_1, workflow=workflow_1, flow=flow)

    case_1 = case_factory(workflow=workflow_1)
    case_2 = case_factory(workflow=workflow_2)

    work_item_1 = work_item_factory(
        task=task_1, status=models.WorkItem.STATUS_READY, child_case=None, case=case_1
    )
    work_item_2 = work_item_factory(
        task=task_1, status=models.WorkItem.STATUS_READY, child_case=None, case=case_2
    )

    api.complete_work_item(work_item_1, admin_user)
    api.complete_work_item(work_item_2, admin_user)

    work_item_1.refresh_from_db()
    work_item_2.refresh_from_db()

    case_1.refresh_from_db()
    case_2.refresh_from_db()

    assert case_1.status == models.Case.STATUS_RUNNING
    assert case_2.status == models.Case.STATUS_COMPLETED


@pytest.mark.parametrize("use_graphql_api", [True, False])
@pytest.mark.parametrize(
    "action,work_item__status,child_case_status,success,expected_status,expected_child_case_status",
    [
        (
            "Cancel",
            models.WorkItem.STATUS_READY,
            None,
            True,
            models.WorkItem.STATUS_CANCELED,
            None,
        ),
        (
            "Cancel",
            models.WorkItem.STATUS_SUSPENDED,
            None,
            True,
            models.WorkItem.STATUS_CANCELED,
            None,
        ),
        (
            "Cancel",
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
            True,
            models.WorkItem.STATUS_CANCELED,
            models.Case.STATUS_CANCELED,
        ),
        (
            "Cancel",
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_SUSPENDED,
            True,
            models.WorkItem.STATUS_CANCELED,
            models.Case.STATUS_CANCELED,
        ),
        (
            "Cancel",
            models.WorkItem.STATUS_SKIPPED,
            None,
            False,
            models.WorkItem.STATUS_SKIPPED,
            None,
        ),
        (
            "Suspend",
            models.WorkItem.STATUS_READY,
            None,
            True,
            models.WorkItem.STATUS_SUSPENDED,
            None,
        ),
        (
            "Suspend",
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
            True,
            models.WorkItem.STATUS_SUSPENDED,
            models.Case.STATUS_SUSPENDED,
        ),
        (
            "Suspend",
            models.WorkItem.STATUS_SKIPPED,
            None,
            False,
            models.WorkItem.STATUS_SKIPPED,
            None,
        ),
        (
            "Resume",
            models.WorkItem.STATUS_READY,
            None,
            False,
            models.WorkItem.STATUS_READY,
            None,
        ),
        (
            "Resume",
            models.WorkItem.STATUS_SKIPPED,
            None,
            False,
            models.WorkItem.STATUS_SKIPPED,
            None,
        ),
        (
            "Resume",
            models.WorkItem.STATUS_SUSPENDED,
            None,
            True,
            models.WorkItem.STATUS_READY,
            None,
        ),
        (
            "Resume",
            models.WorkItem.STATUS_SUSPENDED,
            models.Case.STATUS_SUSPENDED,
            True,
            models.WorkItem.STATUS_READY,
            models.Case.STATUS_RUNNING,
        ),
    ],
)
def test_cancel_suspend_resume_work_item(
    db,
    work_item,
    schema_executor,
    admin_user,
    case_factory,
    use_graphql_api,
    action,
    child_case_status,
    success,
    expected_status,
    expected_child_case_status,
):
    work_item.child_case = child_case_status and case_factory(status=child_case_status)
    work_item.save()

    error_msg = {
        "Cancel": "Only ready or suspended work items can be canceled.",
        "Suspend": "Only ready work items can be suspended.",
        "Resume": "Only suspended work items can be resumed.",
    }[action]
    _action = action.lower()

    if use_graphql_api:
        query = """
            mutation %sWorkItem($input: %sWorkItemInput!) {
                %sWorkItem(input: $input) {
                    clientMutationId
                }
            }
        """ % (
            action,
            action,
            _action,
        )

        result = schema_executor(query, variable_values={"input": {"id": work_item.pk}})

        if success:
            assert not bool(result.errors)
        else:
            assert error_msg in str(result.errors[0])
    else:
        fn = getattr(api, f"{_action}_work_item")

        if success:
            fn(work_item, admin_user)
        else:
            with pytest.raises(ValidationError) as error:
                fn(work_item, admin_user)

            assert error_msg in str(error.value)

    work_item.refresh_from_db()

    assert work_item.status == expected_status

    if expected_child_case_status:
        assert work_item.child_case.status == expected_child_case_status
