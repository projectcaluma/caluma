from caluma.caluma_core.events import on
from caluma.caluma_workflow.events import completed_case, completed_work_item

from .. import models


def test_events(db, work_item_factory, schema_executor):
    work_item = work_item_factory(status=models.WorkItem.STATUS_READY, child_case=None)

    @on(completed_work_item)
    def complete_work_item_event_receiver(sender, work_item, **kwargs):
        work_item.meta = {"been-there": "done that"}
        work_item.save()
        raise Exception("this should not cause an error")

    @on(completed_case)
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
