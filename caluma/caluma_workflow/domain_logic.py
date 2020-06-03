from django.core.exceptions import ValidationError
from django.utils import timezone

from caluma.caluma_core.events import send_event

from ..caluma_form.models import Document
from . import events, models, utils, validators
from .jexl import FlowJexl


class StartCaseLogic:
    """
    Shared domain logic for starting cases.

    Used in the `saveCase` mutation and in the `start_case` API. The logic
    for case creation is split in three parts (`validate_for_start`,
    `pre_start` and `post_start`) so that in between the appropriate create
    method can be called (`super().create(...)` for the serializer and
    `Case.objects.create(...) for the python API`).
    """

    @staticmethod
    def validate_for_start(data):
        form = data.get("form")
        workflow = data.get("workflow")

        if form:
            if (
                not workflow.allow_all_forms
                and not workflow.allow_forms.filter(pk=form.pk).exists()
            ):
                raise ValidationError(
                    f"Workflow {workflow.pk} does not allow to start case with form {form.pk}"
                )

        return data

    @staticmethod
    def pre_start(validated_data, user):
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

    @staticmethod
    def post_start(case, user, parent_work_item):
        # Django doesn't save reverse one-to-one relationships automatically:
        # https://code.djangoproject.com/ticket/18638
        if parent_work_item:
            parent_work_item.child_case = case
            parent_work_item.save()

        workflow = case.workflow
        tasks = workflow.start_tasks.all()

        work_items = utils.bulk_create_work_items(tasks, case, user)

        send_event(events.created_case, sender="case_post_create", case=case)
        for work_item in work_items:  # pragma: no cover
            send_event(
                events.created_work_item, sender="case_post_create", work_item=work_item
            )

        return case


class CompleteWorkItemLogic:
    @staticmethod
    def _can_continue(work_item, task):
        # If a "multiple instance" task has running siblings, the task is not completed
        if task.is_multiple_instance:
            return not work_item.case.work_items.filter(
                task=task, status=models.WorkItem.STATUS_READY
            ).exists()
        return work_item.case.work_items.filter(
            task=task,
            status__in=(
                models.WorkItem.STATUS_COMPLETED,
                models.WorkItem.STATUS_SKIPPED,
            ),
        ).exists()

    @staticmethod
    def validate_for_complete(work_item, user):
        validators.WorkItemValidator().validate(
            status=work_item.status,
            child_case=work_item.child_case,
            task=work_item.task,
            case=work_item.case,
            document=work_item.document,
            user=user,
        )

    @staticmethod
    def pre_complete(validated_data, user):
        validated_data["status"] = models.WorkItem.STATUS_COMPLETED
        validated_data["closed_at"] = timezone.now()
        validated_data["closed_by_user"] = user.username
        validated_data["closed_by_group"] = user.group

        return validated_data

    @staticmethod
    def post_complete(work_item, user):
        case = work_item.case

        if not CompleteWorkItemLogic._can_continue(work_item, work_item.task):
            return work_item

        flow = models.Flow.objects.filter(task_flows__task=work_item.task_id).first()
        flow_referenced_tasks = models.Task.objects.filter(task_flows__flow=flow)

        all_complete = all(
            CompleteWorkItemLogic._can_continue(work_item, task)
            for task in flow_referenced_tasks
        )

        if flow and all_complete:
            jexl = FlowJexl()
            result = jexl.evaluate(flow.next)
            if not isinstance(result, list):
                result = [result]

            tasks = models.Task.objects.filter(pk__in=result)

            created_work_items = utils.bulk_create_work_items(
                tasks, case, user, work_item
            )

            for created_work_item in created_work_items:  # pragma: no cover
                send_event(
                    events.created_work_item,
                    sender="post_complete_work_item",
                    work_item=created_work_item,
                )
        elif not flow and all_complete:
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETED
            case.closed_at = timezone.now()
            case.closed_by_user = user.username
            case.closed_by_group = user.group
            case.save()
            send_event(
                events.completed_case, sender="post_complete_work_item", case=case
            )

        send_event(
            events.completed_work_item,
            sender="post_complete_work_item",
            work_item=work_item,
        )

        return work_item


class SkipWorkItemLogic:
    @staticmethod
    def validate_for_skip(work_item):
        if work_item.status != models.WorkItem.STATUS_READY:
            raise ValidationError("Only READY work items can be skipped")

    @staticmethod
    def pre_skip(validated_data, user):
        validated_data = CompleteWorkItemLogic.pre_complete(validated_data, user)

        validated_data["status"] = models.WorkItem.STATUS_SKIPPED

        return validated_data

    @staticmethod
    def post_skip(work_item, user):
        work_item = CompleteWorkItemLogic.post_complete(work_item, user)

        send_event(
            events.skipped_work_item, sender="post_skip_work_item", work_item=work_item
        )

        return work_item
