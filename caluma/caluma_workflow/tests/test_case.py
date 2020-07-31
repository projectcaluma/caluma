import json

import pytest
from graphql_relay import to_global_id

from ...caluma_core.relay import extract_global_id
from ...caluma_form.models import Question
from .. import api, models


@pytest.mark.parametrize(
    "case__status,result_count",
    [(models.Case.STATUS_RUNNING, 1), (models.Case.STATUS_COMPLETED, 0)],
)
def test_query_all_cases(db, snapshot, case, result_count, flow, schema_executor):
    query = """
        query AllCases {
          allCases (status: RUNNING){
            totalCount
            edges {
              node {
                status
              }
            }
          }
        }
    """
    result = schema_executor(query)

    assert len(result.data["allCases"]["edges"]) == result_count

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("task__lead_time", [100, None])
@pytest.mark.parametrize("task__address_groups", ['["group-name"]|groups', None])
@pytest.mark.parametrize(
    "mutation,update", [("startCase", False), ("saveCase", False), ("saveCase", True)]
)
def test_save_case(
    db,
    snapshot,
    workflow,
    workflow_allow_forms,
    workflow_start_tasks,
    work_item,
    form,
    case,
    schema_executor,
    mutation,
    update,
):

    input_type = {"startCase": "StartCaseInput!", "saveCase": "SaveCaseInput!"}[
        mutation
    ]
    query = """
        mutation StartCase($input: %s) {
          %s (input: $input) {
            case {
              id
              document {
                form {
                  slug
                }
              }
              status
              parentWorkItem {
                status
              }
              workItems {
                edges {
                  node {
                    status
                    addressedGroups
                    document {
                      form {
                        slug
                      }
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """ % (
        input_type,
        mutation,
    )

    inp = {"input": {"workflow": workflow.slug, "form": form.slug}}

    if mutation == "saveCase":
        inp["_context"] = json.dumps({"additional_data": "foo"})

    if update:
        inp["input"]["id"] = str(case.id)

    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    # if it was an update, we expect the same ID else we need a new ID
    is_same_id = extract_global_id(result.data[mutation]["case"]["id"]) == str(case.id)
    assert is_same_id == update

    # can't snapshot IDs, they change
    del result.data[mutation]["case"]["id"]
    snapshot.assert_match(result.data)


def test_start_sub_sub_case(
    db, workflow_factory, work_item_factory, case_factory, schema_executor
):
    workflow = workflow_factory()
    sub_workflow = workflow_factory()
    case = case_factory(workflow=workflow)
    child_case = case_factory(workflow=sub_workflow, family=case)
    work_item_factory(child_case=child_case, case=case)
    sub_work_item = work_item_factory(child_case=None, case=child_case)

    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            case {
              id
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": {"workflow": workflow.slug, "parentWorkItem": str(sub_work_item.pk)}
    }
    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    case_id = result.data["startCase"]["case"]["id"]
    child_child_case = models.Case.objects.get(pk=extract_global_id(case_id))
    assert child_child_case.parent_work_item.pk == sub_work_item.pk
    assert child_child_case.family == child_case.family == case.family == case


def test_start_case_invalid_form(db, workflow, form, schema_executor):
    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            case {
              id
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"workflow": workflow.slug, "form": str(form.pk)}}
    result = schema_executor(query, variable_values=inp)

    assert result.errors


@pytest.mark.parametrize(
    "work_item__status",
    [models.WorkItem.STATUS_COMPLETED, models.WorkItem.STATUS_READY],
)
@pytest.mark.parametrize(
    "case__status,success",
    [(models.Case.STATUS_RUNNING, True), (models.Case.STATUS_COMPLETED, False)],
)
def test_cancel_case(db, snapshot, case, work_item, schema_executor, success):
    query = """
        mutation CancelCase($input: CancelCaseInput!) {
          cancelCase(input: $input) {
            case {
              document {
                form {
                  slug
                }
              }
              status
              workItems {
                edges {
                  node {
                    status
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": case.pk}}
    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "task__is_multiple_instance,task__address_groups,count",
    [(False, ["group1", "group2"], 1), (True, ["group1", "group2"], 2)],
)
def test_multiple_instance_task_address_groups(
    db, workflow, workflow_start_tasks, task, count, schema_executor
):
    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            clientMutationId
          }
        }
    """

    inp = {"input": {"workflow": workflow.slug}}
    result = schema_executor(query, variable_values=inp)
    assert not bool(result.errors)
    assert models.WorkItem.objects.count() == count


def test_status_filter(db, case_factory, schema_executor):
    case_factory(status=models.Case.STATUS_CANCELED)
    case_factory(status=models.Case.STATUS_COMPLETED)
    case_factory(status=models.Case.STATUS_RUNNING)

    query = """
        query AllCases {
          allCases (status: [RUNNING, CANCELED]){
            totalCount
            edges {
              node {
                status
              }
            }
          }
        }
    """
    result = schema_executor(query)

    expected = ["CANCELED", "RUNNING"]
    received = sorted(
        [edge["node"]["status"] for edge in result.data["allCases"]["edges"]]
    )

    assert expected == received


def test_root_case_filter(schema_executor, db, workflow_factory, case_factory):
    workflow = workflow_factory()
    sub_workflow = workflow_factory()
    other_workflow = workflow_factory()
    case = case_factory(workflow=workflow)
    child_case = case_factory(workflow=sub_workflow, family=case)
    case_factory(workflow=other_workflow)  # dummy case that should not be returned

    query = """
        query AllCases ($case: ID!) {
          allCases(rootCase: $case) {
            edges {
              node {
                id
              }
            }
          }
        }
    """
    variables = {"case": case.pk}
    result = schema_executor(query, variable_values=variables)

    assert not result.errors

    result_ids = [
        extract_global_id(edge["node"]["id"])
        for edge in result.data["allCases"]["edges"]
    ]

    assert sorted(result_ids) == sorted([str(case.id), str(child_case.id)])


def test_family_workitems(schema_executor, db, case_factory, work_item_factory):
    case = case_factory()
    child_case = case_factory(family=case)
    dummy_case = case_factory()
    work_item = work_item_factory(child_case=child_case, case=case)
    sub_work_item = work_item_factory(child_case=None, case=child_case)
    work_item_factory(child_case=None, case=dummy_case)

    query = """
        query CaseNode ($case: ID!) {
          node(id: $case) {
            ...on Case {
              familyWorkItems {
                edges {
                  node {
                    id
                  }
                }
              }
            }
          }
        }
    """

    variables = {"case": to_global_id("Case", case.pk)}
    result = schema_executor(query, variable_values=variables)

    assert not result.errors

    result_ids = [
        extract_global_id(edge["node"]["id"])
        for edge in result.data["node"]["familyWorkItems"]["edges"]
    ]

    assert sorted(result_ids) == sorted([str(work_item.id), str(sub_work_item.id)])


@pytest.mark.parametrize("asc", [True, False])
@pytest.mark.parametrize(
    "type,success",
    [
        (Question.TYPE_TEXT, True),
        (Question.TYPE_FORM, True),
        (Question.TYPE_DATE, True),
        (Question.TYPE_FILE, True),
        (Question.TYPE_TABLE, False),
    ],
)
def test_order_by_question_answer_value(
    db,
    snapshot,
    schema_executor,
    asc,
    type,
    success,
    case_factory,
    document_factory,
    question_factory,
    form_question_factory,
    form_factory,
    answer_factory,
):
    value = "test_question1"

    if type == Question.TYPE_TEXT:
        d1 = document_factory()
        d2 = document_factory()
        d3 = document_factory()

        q1 = question_factory(type=Question.TYPE_TEXT, slug="test_question1")
        answer_factory(question=q1, value="c", document=d1)
        answer_factory(question=q1, value="a", document=d2)
        answer_factory(question=q1, value="b", document=d3)

        q2 = question_factory(type=Question.TYPE_TEXT, slug="test_question2")
        answer_factory(question=q2, value="a2", document=d1)
        answer_factory(question=q2, value="b2", document=d2)
        answer_factory(question=q2, value="c2", document=d3)

        case_factory(document=d1)
        case_factory(document=d2)
        case_factory(document=d3)

    elif type == Question.TYPE_FORM:
        value = "test_sub_question1"

        f = form_factory(slug="test_sub_form")
        question = question_factory(type=Question.TYPE_TEXT, slug="test_sub_question1")
        form_question_factory(form=f, question=question)

        d1 = document_factory(form=f)
        answer_factory(question=question, value="d", document=d1)

        d2 = document_factory(form=f)
        answer_factory(question=question, value="b", document=d2)

        d3 = document_factory(form=f)
        answer_factory(question=question, value="f", document=d3)

        form_question = question_factory(
            type=Question.TYPE_FORM, slug="test_form_question", sub_form=f
        )

        form_question_factory(question=form_question)

        case_factory(document=d1)

        case_factory(document=d2)

        case_factory(document=d3)

        # add another form_question and corresponding answers
        form_question_factory(question=question)
        answer_factory(question=question, value="c")
        answer_factory(question=question, value="e")
        answer_factory(question=question, value="a")

    elif type == Question.TYPE_DATE:
        d1 = document_factory()
        d2 = document_factory()
        d3 = document_factory()

        q1 = question_factory(type=Question.TYPE_DATE, slug="test_question1")
        answer_factory(question=q1, date="2019-05-31", document=d1)
        answer_factory(question=q1, date="2019-05-29", document=d2)
        answer_factory(question=q1, date="2019-05-27", document=d3)

        q2 = question_factory(type=Question.TYPE_DATE, slug="test_question2")
        answer_factory(question=q2, date="2019-05-26", document=d1)
        answer_factory(question=q2, date="2019-05-30", document=d2)
        answer_factory(question=q2, date="2019-05-28", document=d3)

        case_factory(document=d1)
        case_factory(document=d2)
        case_factory(document=d3)

    elif type == Question.TYPE_FILE:
        d1 = document_factory()
        d2 = document_factory()
        d3 = document_factory()

        q1 = question_factory(type=Question.TYPE_FILE, slug="test_question1")
        answer_factory(question=q1, file__name="d", document=d1)
        answer_factory(question=q1, file__name="b", document=d2)
        answer_factory(question=q1, file__name="f", document=d3)

        q2 = question_factory(type=Question.TYPE_FILE, slug="test_question2")
        answer_factory(question=q2, file__name="c", document=d1)
        answer_factory(question=q2, file__name="e", document=d2)
        answer_factory(question=q2, file__name="a", document=d3)

        case_factory(document=d1)
        case_factory(document=d2)
        case_factory(document=d3)

    elif type == Question.TYPE_TABLE:
        d1 = document_factory()
        question_factory(type=Question.TYPE_TABLE, slug="test_question1")
        case_factory(document=d1)

    # It's necessary to order the answers by "CREATED_AT_ASC" in order to every time
    # produce the same response
    query = """
        query AllCases($orderByQuestionAnswerValue: String) {
          allCases(orderByQuestionAnswerValue: $orderByQuestionAnswerValue){
            totalCount
            edges {
              node {
                document {
                  answers(orderBy: CREATED_AT_ASC) {
                    totalCount
                    edges {
                      node {
                        ... on StringAnswer {
                          stringValue: value
                        }
                        ... on DateAnswer {
                          dateValue: value
                        }
                        ... on FileAnswer {
                          fileValue: value {
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    if not asc:
        value = f"-{value}"

    inp = {"orderByQuestionAnswerValue": value}

    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success
    if success:
        assert result.data["allCases"]["totalCount"] == 3
        snapshot.assert_match(result.data)


def test_document_form(
    db, schema_executor, case_factory, document_factory, form_factory
):

    form_a, form_b = form_factory.create_batch(2)

    # two cases, one for each form
    case_factory(document=document_factory(form=form_a))
    case_factory(document=document_factory(form=form_b))

    query = """
        query AllCases ($form: String!) {
          allCases (documentForm: $form){
            totalCount
            edges {
              node {
                document {
                  form {
                    id
                  }
                }
              }
            }
          }
        }
    """
    # search for form A's slug
    result = schema_executor(query, variable_values={"form": form_a.slug})

    assert len(result.data["allCases"]["edges"]) == 1

    assert not result.errors

    document = result.data["allCases"]["edges"][0]["node"]["document"]

    assert extract_global_id(document["form"]["id"]) == form_a.slug


@pytest.mark.parametrize("question__slug,question__type", [("asdf", "text")])
@pytest.mark.parametrize("form__slug", ["theform"])
@pytest.mark.parametrize(
    "doc_val,workitem_val,result_count", [("hello", "blah", 0), ("blah", "hello", 1)]
)
def test_work_item_document(
    db,
    case,
    form,
    work_item_factory,
    answer_factory,
    question,
    schema_executor,
    doc_val,
    workitem_val,
    result_count,
):
    work_item = work_item_factory(document__form=form, case=case)
    answer_factory(document=work_item.document, question=question, value=workitem_val)
    answer_factory(document=case.document, question=question, value=doc_val)

    query = """
        query workitems ($filter: HasAnswerFilterType){
          allCases(filter: [
            {workItemDocumentHasAnswer: [$filter]}
          ]) {
            edges {
              node {
                id
              }
            }
          }
        }

    """
    result = schema_executor(
        query,
        variable_values={
            "filter": {"question": question.slug, "value": "hello", "lookup": "EXACT"}
        },
    )

    assert not result.errors

    assert len(result.data["allCases"]["edges"]) == result_count


@pytest.mark.parametrize("task__lead_time", [100, None])
@pytest.mark.parametrize("task__address_groups", ['["group-name"]|groups', None])
def test_api_start_case(
    db,
    workflow,
    workflow_allow_forms,
    workflow_start_tasks,
    work_item,
    task,
    form,
    case,
    admin_user,
):
    case = api.start_case(workflow=workflow, form=form, user=admin_user)
    work_item = case.work_items.get(task_id=task.pk)

    assert case.document.form == form
    assert work_item.document.form == form
    assert work_item.status == models.WorkItem.STATUS_READY


@pytest.mark.parametrize(
    "case__status,work_item__status",
    [(models.Case.STATUS_RUNNING, models.WorkItem.STATUS_READY)],
)
def test_api_cancel_case(db, case, work_item, admin_user):
    api.cancel_case(case=case, user=admin_user)

    case.refresh_from_db()
    work_item.refresh_from_db()

    assert case.status == models.Case.STATUS_CANCELED
    assert work_item.status == models.WorkItem.STATUS_CANCELED
