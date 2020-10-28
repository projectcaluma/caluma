from typing import Optional

from caluma.caluma_form.models import Form
from caluma.caluma_user.models import BaseUser
from caluma.utils import update_model

from . import domain_logic, models


def start_case(
    workflow: models.Workflow,
    user: BaseUser,
    form: Optional[Form] = None,
    parent_work_item: Optional[models.WorkItem] = None,
    context: Optional[dict] = None,
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

    return domain_logic.StartCaseLogic.post_start(case, user, parent_work_item, context)


def complete_work_item(
    work_item: models.WorkItem, user: BaseUser, context: Optional[dict] = None
) -> models.WorkItem:
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
    validated_data = domain_logic.CompleteWorkItemLogic.pre_complete(
        work_item, {}, user, context
    )

    update_model(work_item, validated_data)

    domain_logic.CompleteWorkItemLogic.post_complete(work_item, user, context)

    return work_item


def skip_work_item(
    work_item: models.WorkItem, user: BaseUser, context: Optional[dict] = None
) -> models.WorkItem:
    """
    Skip a work item (just like `SkipWorkItem`).

    >>> skip_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    """
    domain_logic.SkipWorkItemLogic.validate_for_skip(work_item)

    validated_data = domain_logic.SkipWorkItemLogic.pre_skip(
        work_item, {}, user, context
    )

    update_model(work_item, validated_data)

    domain_logic.SkipWorkItemLogic.post_skip(work_item, user, context)

    return work_item


def cancel_case(
    case: models.Case, user: BaseUser, context: Optional[dict] = None
) -> models.Case:
    """
    Cancel a case and its pending work items (just like `CancelCase`).

    >>> cancel_case(
    ...     case=models.Case.first(),
    ...     user=AnonymousUser()
    ... )
    <Case: Case object (some-uuid)>
    """
    domain_logic.CancelCaseLogic.validate_for_cancel(case)

    validated_data = domain_logic.CancelCaseLogic.pre_cancel(case, {}, user, context)

    update_model(case, validated_data)

    domain_logic.CancelCaseLogic.post_cancel(case, user, context)

    return case


def cancel_work_item(
    work_item: models.WorkItem, user: BaseUser, context: Optional[dict] = None
) -> models.WorkItem:
    """
    Cancel a work item (just like `CancelWorkItem`).

    >>> cancel_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    """
    domain_logic.CancelWorkItemLogic.validate_for_cancel(work_item)

    validated_data = domain_logic.CancelWorkItemLogic.pre_cancel(
        work_item, {}, user, context
    )

    update_model(work_item, validated_data)

    domain_logic.CancelWorkItemLogic.post_cancel(work_item, user, context)

    return work_item


def suspend_case(
    case: models.Case, user: BaseUser, context: Optional[dict] = None
) -> models.Case:
    """
    Suspend a case (just like `SuspendCase`).

    >>> suspend_case(
    ...     case=models.Case.first(),
    ...     user=AnonymousUser()
    ... )
    <Case: Case object (some-uuid)>
    """
    domain_logic.SuspendCaseLogic.validate_for_suspend(case)

    validated_data = domain_logic.SuspendCaseLogic.pre_suspend(case, {}, user, context)

    update_model(case, validated_data)

    domain_logic.SuspendCaseLogic.post_suspend(case, user, context)

    return case


def suspend_work_item(
    work_item: models.WorkItem, user: BaseUser, context: Optional[dict] = None
) -> models.WorkItem:
    """
    Suspend a work item (just like `SuspendWorkItem`).

    >>> suspend_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    """
    domain_logic.SuspendWorkItemLogic.validate_for_suspend(work_item)

    validated_data = domain_logic.SuspendWorkItemLogic.pre_suspend(
        work_item, {}, user, context
    )

    update_model(work_item, validated_data)

    domain_logic.SuspendWorkItemLogic.post_suspend(work_item, user, context)

    return work_item


def resume_case(
    case: models.Case, user: BaseUser, context: Optional[dict] = None
) -> models.Case:
    """
    Resume a case (just like `ResumeCase`).

    >>> resume_case(
    ...     case=models.Case.first(),
    ...     user=AnonymousUser()
    ... )
    <Case: Case object (some-uuid)>
    """
    domain_logic.ResumeCaseLogic.validate_for_resume(case)

    validated_data = domain_logic.ResumeCaseLogic.pre_resume(case, {}, user, context)

    update_model(case, validated_data)

    domain_logic.ResumeCaseLogic.post_resume(case, user, context)

    return case


def resume_work_item(
    work_item: models.WorkItem, user: BaseUser, context: Optional[dict] = None
) -> models.WorkItem:
    """
    Resume a work item (just like `ResumeWorkItem`).

    >>> resume_work_item(
    ...     work_item=models.WorkItem.first(),
    ...     user=AnonymousUser()
    ... )
    <WorkItem: WorkItem object (some-uuid)>
    """
    domain_logic.ResumeWorkItemLogic.validate_for_resume(work_item)

    validated_data = domain_logic.ResumeWorkItemLogic.pre_resume(
        work_item, {}, user, context
    )

    update_model(work_item, validated_data)

    domain_logic.ResumeWorkItemLogic.post_resume(work_item, user, context)

    return work_item
