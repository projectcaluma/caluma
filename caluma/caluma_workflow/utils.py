from simple_history.utils import bulk_create_with_history

from ..caluma_form.models import Document
from . import models
from .jexl import FlowJexl, GroupJexl


def get_group_jexl_structure(work_item_created_by_group, case, prev_work_item=None):
    return {
        "case": {"created_by_group": case.created_by_group},
        "work_item": {"created_by_group": work_item_created_by_group},
        "prev_work_item": {
            "controlling_groups": prev_work_item.controlling_groups
            if prev_work_item
            else None
        },
    }


def get_jexl_groups(
    jexl, task, case, work_item_created_by_user, prev_work_item=None, context=None
):
    if jexl:
        return GroupJexl(
            validation_context=get_group_jexl_structure(
                work_item_created_by_user.group, case, prev_work_item
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


def bulk_create_work_items(
    tasks, case, user, prev_work_item=None, context: dict = None
):
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
        addressed_groups = [
            get_jexl_groups(
                task.address_groups,
                task,
                case,
                user,
                prev_work_item if prev_work_item else None,
                context,
            )
        ]
        if task.is_multiple_instance:
            addressed_groups = [[x] for x in addressed_groups[0]]

        for groups in addressed_groups:
            work_items.append(
                models.WorkItem(
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

    bulk_create_with_history(work_items, models.WorkItem)
    return work_items
