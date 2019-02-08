import pytest

from .. import models
from ...core.relay import extract_global_id


def test_query_all_cases(db, snapshot, case, flow, schema_executor):
    query = """
        query AllCases {
          allCases {
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


@pytest.mark.parametrize("task__address_groups", ['["group-name"]|groups', None])
def test_start_case(
    db,
    snapshot,
    workflow,
    workflow_allow_forms,
    workflow_start_tasks,
    work_item,
    form,
    schema_executor,
):
    query = """
        mutation StartCase($input: StartCaseInput!) {
          startCase(input: $input) {
            case {
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
    """

    inp = {"input": {"workflow": workflow.slug, "form": form.slug}}
    result = schema_executor(query, variables=inp)

    assert not result.errors
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
