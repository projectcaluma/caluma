from typing import Optional

from caluma.caluma_form.models import Form
from caluma.caluma_user.models import BaseUser

from . import domain_logic, models


def start_case(
    workflow: models.Workflow,
    user: BaseUser,
    form: Optional[Form] = None,
    parent_work_item: Optional[models.WorkItem] = None,
    **kwargs
) -> models.Case:
    """
    Start a case of a given workflow (just like `saveCase`).

    Similar to Case.objects.create(), but with the same business logic as
    used in the `saveCase` mutation.

    >>> start_case(
    ...     workflow=Workflow.objects.get(pk="my-wf"),
    ...     form=Form.objects.get(pk="my-form")),
    ...     user=AnonymousUser()
    ... )
    <Case: Case object (some-uuid)>
    """
    data = {"workflow": workflow, "form": form, "parent_work_item": parent_work_item}

    data.update(kwargs)

    validated_data = domain_logic.StartCaseLogic.pre_start(
        domain_logic.StartCaseLogic.validate_for_start(data), user
    )

    case = models.Case.objects.create(**validated_data)

    return domain_logic.StartCaseLogic.post_start(case, user, parent_work_item)


def complete_work_item(work_item: models.WorkItem, user: BaseUser) -> models.WorkItem:
    """
    Complete a work item (just like `completeWorkItem`).

    >>> complete_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    ```
    """
    domain_logic.CompleteWorkItemLogic.validate_for_complete(work_item, user)
    validated_data = domain_logic.CompleteWorkItemLogic.pre_complete({}, user)

    models.WorkItem.objects.filter(pk=work_item.pk).update(**validated_data)

    domain_logic.CompleteWorkItemLogic.post_complete(work_item, user)

    return work_item


def skip_work_item(work_item: models.WorkItem, user: BaseUser) -> models.WorkItem:
    """
    Skip a work item (just like `SkipWorkItem`).

    >>> skip_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    """
    domain_logic.SkipWorkItemLogic.validate_for_skip(work_item)

    validated_data = domain_logic.SkipWorkItemLogic.pre_skip({}, user)

    models.WorkItem.objects.filter(pk=work_item.pk).update(**validated_data)

    domain_logic.SkipWorkItemLogic.post_skip(work_item, user)

    return work_item
