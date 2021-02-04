import pytest

from caluma.caluma_core.events import SignalHandlingError, on
from caluma.caluma_workflow.api import skip_work_item
from caluma.caluma_workflow.events import (
    post_complete_case,
    post_complete_work_item,
    post_skip_work_item,
)
from caluma.caluma_workflow.models import WorkItem


def test_events(db, work_item_factory, schema_executor):
    work_item = work_item_factory(status=WorkItem.STATUS_READY, child_case=None)

    @on(post_complete_work_item)
    def complete_work_item_event_receiver(sender, work_item, **kwargs):
        work_item.meta = {"been-there": "done that"}
        work_item.save()
        raise Exception("this should not cause an error")

    @on(post_complete_case)
    def complete_case_event_receiver(sender, case, **kwargs):
        case.meta = {"been-there": "done that"}
        case.save()

    query = """
        mutation CompleteWorkItem($input: CompleteWorkItemInput!) {
          completeWorkItem(input: $input) {
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": work_item.pk}}
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    work_item.refresh_from_db()
    assert work_item.meta == {"been-there": "done that"}
    assert work_item.case.meta == {"been-there": "done that"}


def test_skip_event(db, work_item_factory, schema_executor):
    work_item = work_item_factory(status=WorkItem.STATUS_READY, child_case=None)

    @on(post_complete_work_item)
    def complete_work_item_event_receiver(sender, work_item, **kwargs):
        raise AssertionError(
            "complete event handler should not have been called!"
        )  # pragma: no cover

    @on(post_skip_work_item)
    def skip_work_item_event_receiver(sender, work_item, **kwargs):
        work_item.meta = {"been-there": "done that"}
        work_item.save()

    query = """
        mutation SkipWorkItem($input: SkipWorkItemInput!) {
          skipWorkItem(input: $input) {
            clientMutationId
          }
        }
    """

    inp = {"input": {"id": work_item.pk}}
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    work_item.refresh_from_db()
    assert work_item.meta == {"been-there": "done that"}


@pytest.mark.parametrize(
    "event,raise_exception",
    [
        (post_skip_work_item, False),
        (post_skip_work_item, True),
        ([post_skip_work_item], True),
    ],
)
def test_event_raise_exceptions(
    db, admin_user, work_item_factory, event, raise_exception
):
    work_item = work_item_factory(status=WorkItem.STATUS_READY, child_case=None)

    @on(event, raise_exception=raise_exception)
    def receiver1(sender, **kwargs):
        raise AssertionError("Error 1")

    @on(event, raise_exception=raise_exception)
    def receiver2(sender, **kwargs):
        raise AssertionError("Error 2")

    if raise_exception:
        with pytest.raises(SignalHandlingError) as exc:
            skip_work_item(work_item, admin_user)

        assert str(exc.value) == "Error 1, Error 2"
    else:
        assert skip_work_item(work_item, admin_user)
