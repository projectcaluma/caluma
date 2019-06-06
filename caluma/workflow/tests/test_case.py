import pytest

from ...core.relay import extract_global_id
from ...form.models import Question
from .. import models


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
@pytest.mark.parametrize("mutation", ["startCase", "saveCase"])
def test_start_case(
    db,
    snapshot,
    workflow,
    workflow_allow_forms,
    workflow_start_tasks,
    work_item,
    form,
    schema_executor,
    mutation,
    case,
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
        inp["input"]["id"] = str(case.id)

    result = schema_executor(query, variables=inp)

    assert not result.errors

    # if StartCase, we need a new ID, if "saveCase", we expect the same ID
    id_needs_to_be_same = mutation == "saveCase"
    is_same_id = extract_global_id(result.data[mutation]["case"]["id"]) == str(case.id)
    assert is_same_id == id_needs_to_be_same

    # can't snapshot IDs, they change
    del result.data[mutation]["case"]["id"]
    snapshot.assert_match(result.data)


def test_start_sub_case(db, workflow, work_item, schema_executor):
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

    inp = {"input": {"workflow": workflow.slug, "parentWorkItem": str(work_item.pk)}}
    result = schema_executor(query, variables=inp)

    assert not result.errors

    case_id = result.data["startCase"]["case"]["id"]
    case = models.Case.objects.get(pk=extract_global_id(case_id))
    assert case.parent_work_item.pk == work_item.pk


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
    result = schema_executor(query, variables=inp)

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
    result = schema_executor(query, variables=inp)

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
    result = schema_executor(query, variables=inp)
    assert not bool(result.errors)
    assert models.WorkItem.objects.count() == count


def test_start_case_with_child_documents(
    db,
    workflow,
    workflow_allow_forms,
    workflow_start_tasks,
    task,
    form,
    form_question_factory,
    question_factory,
    schema_executor,
):
    sub_form_question = form_question_factory(question__type=Question.TYPE_FORM)
    question = question_factory(
        type=Question.TYPE_FORM, sub_form=sub_form_question.form
    )
    form_question = form_question_factory(form=form, question=question)

    query = """
        mutation StartCase($input: StartCaseInput!) {
            startCase(input: $input) {
                case {
                    id
                    document {
                        id
                        answers {
                            totalCount
                            edges {
                                node {
                                    id
                                    ... on FormAnswer {
                                        value {
                                            id
                                            answers {
                                                totalCount
                                                edges {
                                                    node {
                                                        id
                                                        ... on FormAnswer {
                                                            value {
                                                                id
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
                    }
                }
            }
        }
    """

    inp = {"input": {"workflow": workflow.slug, "form": form_question.form.pk}}
    result = schema_executor(query, variables=inp)
    assert not result.errors
    sub_document = result.data["startCase"]["case"]["document"]["answers"]["edges"][0][
        "node"
    ]
    assert sub_document["id"]
    assert sub_document["value"]["answers"]["edges"][0]["node"]["id"]


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
    assert result.data["allCases"]["totalCount"] == 2
    assert result.data["allCases"]["edges"][0]["node"]["status"] == "CANCELED"
    assert result.data["allCases"]["edges"][1]["node"]["status"] == "RUNNING"
