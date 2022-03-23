from ..caluma_form.models import Document
from . import models
from .jexl import FlowJexl, GroupJexl


def get_group_jexl_structure(
    work_item_created_by_group, case, prev_work_item=None, context=None
):
    return {
        "case": {"created_by_group": case.created_by_group},
        "work_item": {"created_by_group": work_item_created_by_group},
        "prev_work_item": {
            "addressed_groups": prev_work_item.addressed_groups
            if prev_work_item
            else None,
            "controlling_groups": prev_work_item.controlling_groups
            if prev_work_item
            else None,
        },
        "context": {
            "addressed_groups": context.get("addressed_groups") if context else None,
            "controlling_groups": context.get("controlling_groups")
            if context
            else None,
        },
    }


def get_jexl_groups(
    jexl, task, case, work_item_created_by_user, prev_work_item=None, context=None
):
    if jexl:
        return GroupJexl(
            validation_context=get_group_jexl_structure(
                work_item_created_by_user.group, case, prev_work_item, context
            ),
            task=task,
            case=case,
            work_item_created_by_user=work_item_created_by_user,
            prev_work_item=prev_work_item,
            dynamic_context=context,
        ).evaluate(jexl)

    return []


def get_jexl_tasks(jexl, case, user, prev_work_item, context=None):
    if jexl:
        evaluated = FlowJexl(
            case=case, user=user, prev_work_item=prev_work_item, dynamic_context=context
        ).evaluate(jexl)

        if not isinstance(evaluated, list):
            evaluated = [evaluated]

        return evaluated

    return []


def create_work_items(tasks, case, user, prev_work_item=None, context: dict = None):
    work_items = []

    for task in tasks:
        controlling_groups = get_jexl_groups(
            task.control_groups,
            task,
            case,
            user,
            prev_work_item if prev_work_item else None,
            context,
        )
        addressed_groups = get_jexl_groups(
            task.address_groups,
            task,
            case,
            user,
            prev_work_item if prev_work_item else None,
            context,
        )
        if task.is_multiple_instance:
            # for multiple instance tasks, create one work item per adressed group
            work_item_groups = [[group] for group in addressed_groups]

            # make sure that at least one work item is always created, even if addressed_groups is empty
            if not work_item_groups:
                work_item_groups = [[]]
        else:
            # for regular tasks, multiple groups can be adressed to one work item
            work_item_groups = [addressed_groups]

        for groups in work_item_groups:
            if (
                not task.is_multiple_instance
                and models.WorkItem.objects.filter(
                    addressed_groups=groups,
                    controlling_groups=controlling_groups,
                    task_id=task.pk,
                    case=case,
                    status__in=[
                        models.WorkItem.STATUS_READY,
                        models.WorkItem.STATUS_SUSPENDED,
                    ],
                ).exists()
            ):
                # work item already exists, do not create a new one
                continue

            work_items.append(
                models.WorkItem.objects.create(
                    addressed_groups=groups,
                    controlling_groups=controlling_groups,
                    task_id=task.pk,
                    deadline=task.calculate_deadline(),
                    document=Document.objects.create_document_for_task(task, user),
                    case=case,
                    status=models.WorkItem.STATUS_READY,
                    created_by_user=user.username,
                    created_by_group=user.group,
                    previous_work_item=prev_work_item if prev_work_item else None,
                )
            )

    return work_items
