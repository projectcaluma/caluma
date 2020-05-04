from django.db.models import Manager
from caluma.caluma_core.events import send_event
from ..caluma_form.models import Document, Form
from . import events, models
from .jexl import FlowJexl, GroupJexl
from simple_history.utils import bulk_create_with_history


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


def get_jexl_groups(jexl, case, work_item_created_by_group, prev_work_item=None):
    context = get_group_jexl_structure(work_item_created_by_group, case, prev_work_item)
    if jexl:
        return GroupJexl(validation_context=context).evaluate(jexl)
    return []


def bulk_create_work_items(tasks, case, user, prev_work_item=None):
    work_items = []
    for task in tasks:
        controlling_groups = get_jexl_groups(
            task.control_groups,
            case,
            user.group,
            prev_work_item if prev_work_item else None,
        )
        addressed_groups = [
            get_jexl_groups(
                task.address_groups,
                case,
                user.group,
                prev_work_item if prev_work_item else None,
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
                )
            )

    bulk_create_with_history(work_items, models.WorkItem)
    return work_items


class CaseManager(Manager):
    def _validate(self, data):
        form = data.get("form")
        workflow = data.get("workflow")

        if form:
            if (
                not workflow.allow_all_forms
                and not workflow.allow_forms.filter(pk=form.pk).exists()
            ):
                raise Exception(
                    f"Workflow {workflow.pk} does not allow to start case with form {form.pk}"
                )

        return data

    def _pre_create(self, validated_data, user):
        parent_work_item = validated_data.get("parent_work_item")
        validated_data["status"] = models.Case.STATUS_RUNNING

        form = validated_data.pop("form", None)
        if form:
            validated_data["document"] = Document.objects.create(
                form=form, created_by_user=user.username, created_by_group=user.group
            )

        if parent_work_item:
            case = parent_work_item.case
            while hasattr(case, "parent_work_item"):
                case = case.parent_work_item.case
            validated_data["family"] = case

        return validated_data

    def _post_create(self, case, user, parent_work_item):
        # Django doesn't save reverse one-to-one relationships automatically:
        # https://code.djangoproject.com/ticket/18638
        if parent_work_item:
            parent_work_item.child_case = case
            parent_work_item.save()

        workflow = case.workflow
        tasks = workflow.start_tasks.all()

        work_items = bulk_create_work_items(tasks, case, user)

        send_event(events.created_case, sender="case_post_create", case=case)
        for work_item in work_items:  # pragma: no cover
            send_event(
                events.created_work_item, sender="case_post_create", work_item=work_item
            )

        return case

    def start(self, *args, **kwargs):
        user = kwargs.pop("user")

        validated_data = self._pre_create(self._validate(kwargs), user)

        case = self.create(**kwargs)

        return self._post_create(case, user, validated_data.get("parent_work_item"))
