from django.core.exceptions import ValidationError
from django.utils import timezone

from caluma.caluma_form.models import Document

from . import api, models, utils, validators
from .events import send_event_with_deprecations


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
    def pre_start(validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_create_case",
            sender="pre_create_case",
            case=None,
            validated_data=validated_data,
            user=user,
            context=context,
        )

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
    def post_start(case, user, parent_work_item, context=None):
        # Django doesn't save reverse one-to-one relationships automatically:
        # https://code.djangoproject.com/ticket/18638
        if parent_work_item:
            parent_work_item.child_case = case
            parent_work_item.save()

        workflow = case.workflow
        tasks = workflow.start_tasks.all()

        work_items = utils.bulk_create_work_items(tasks, case, user, None, context)

        send_event_with_deprecations(
            "post_create_case",
            sender="case_post_create",
            case=case,
            user=user,
            context=context,
        )

        for work_item in work_items:  # pragma: no cover
            send_event_with_deprecations(
                "post_create_work_item",
                sender="case_post_create",
                work_item=work_item,
                user=user,
                context=context,
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
    def pre_complete(
        work_item,
        validated_data,
        user,
        context=None,
        event="pre_complete_work_item",
        sender="pre_complete_work_item",
    ):
        send_event_with_deprecations(
            event, sender=sender, work_item=work_item, user=user, context=context
        )

        validated_data["status"] = models.WorkItem.STATUS_COMPLETED
        validated_data["closed_at"] = timezone.now()
        validated_data["closed_by_user"] = user.username
        validated_data["closed_by_group"] = user.group

        return validated_data

    @staticmethod
    def post_complete(
        work_item,
        user,
        context=None,
        event="post_complete_work_item",
        sender="post_complete_work_item",
    ):
        case = work_item.case

        send_event_with_deprecations(
            event, sender=sender, work_item=work_item, user=user, context=context
        )

        if not CompleteWorkItemLogic._can_continue(work_item, work_item.task):
            return work_item

        flow = models.Flow.objects.filter(
            task_flows__task=work_item.task_id,
            task_flows__workflow=work_item.case.workflow.pk,
        ).first()

        next_tasks = models.Task.objects.filter(
            pk__in=utils.get_jexl_tasks(
                flow.next if flow else None, work_item.case, user, work_item, context
            )
        )

        if next_tasks.exists():
            sibling_tasks = models.Task.objects.filter(task_flows__flow=flow)

            all_siblings_complete = all(
                CompleteWorkItemLogic._can_continue(work_item, task)
                for task in sibling_tasks
            )

            if all_siblings_complete:
                created_work_items = utils.bulk_create_work_items(
                    next_tasks, case, user, work_item, context
                )

                for created_work_item in created_work_items:  # pragma: no cover
                    send_event_with_deprecations(
                        "post_create_work_item",
                        sender=sender,
                        work_item=created_work_item,
                        user=user,
                        context=context,
                    )

        if (
            not next_tasks.exists()
            and not work_item.case.work_items.filter(
                status=models.WorkItem.STATUS_READY
            ).exists()
        ):
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETED
            case.closed_at = timezone.now()
            case.closed_by_user = user.username
            case.closed_by_group = user.group
            case.save()

            send_event_with_deprecations(
                "post_complete_case",
                sender=sender,
                case=case,
                user=user,
                context=context,
            )

        return work_item


class SkipWorkItemLogic:
    @staticmethod
    def validate_for_skip(work_item):
        if work_item.case.status != models.Case.STATUS_RUNNING:
            raise ValidationError("Only work items of running cases can be skipped.")

        if work_item.status != models.WorkItem.STATUS_READY:
            raise ValidationError("Only ready work items can be skipped.")

    @staticmethod
    def pre_skip(work_item, validated_data, user, context=None):
        validated_data = CompleteWorkItemLogic.pre_complete(
            work_item,
            validated_data,
            user,
            context,
            event="pre_skip_work_item",
            sender="pre_skip_work_item",
        )

        validated_data["status"] = models.WorkItem.STATUS_SKIPPED

        if (
            work_item.child_case
            and work_item.child_case.status == models.Case.STATUS_RUNNING
        ):
            api.cancel_case(work_item.child_case, user, context)

        return validated_data

    @staticmethod
    def post_skip(work_item, user, context=None):
        work_item = CompleteWorkItemLogic.post_complete(
            work_item,
            user,
            context,
            event="post_skip_work_item",
            sender="post_skip_work_item",
        )

        return work_item


class CancelCaseLogic:
    """
    Shared domain logic for canceling cases.

    Used in the `cancelCase` mutation and in the `cancel_case` API. The logic
    for case cancelation is split in three parts (`validate_for_cancel`,
    `pre_cancel` and `post_cancel`) so that in between the appropriate update
    method can be called (`super().update(...)` for the serializer and
    `Case.objects.update(...) for the python API`).
    """

    @staticmethod
    def validate_for_cancel(case):
        if case.status not in [
            models.Case.STATUS_RUNNING,
            models.Case.STATUS_SUSPENDED,
        ]:
            raise ValidationError("Only running or suspended cases can be canceled.")

    @staticmethod
    def pre_cancel(case, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_cancel_case",
            sender="pre_cancel_case",
            case=case,
            user=user,
            context=context,
        )

        validated_data["status"] = models.Case.STATUS_CANCELED
        validated_data["closed_at"] = timezone.now()
        validated_data["closed_by_user"] = user.username
        validated_data["closed_by_group"] = user.group

        for work_item in case.work_items.filter(
            status__in=[models.WorkItem.STATUS_READY, models.WorkItem.STATUS_SUSPENDED]
        ):
            api.cancel_work_item(work_item, user, context)

        return validated_data

    @staticmethod
    def post_cancel(case, user, context=None):
        send_event_with_deprecations(
            "post_cancel_case",
            sender="post_cancel_case",
            case=case,
            user=user,
            context=context,
        )

        return case


class SuspendCaseLogic:
    """
    Shared domain logic for suspending cases.

    Used in the `suspendCase` mutation and in the `suspend_case` API. The logic
    for case suspension is split in three parts (`validate_for_suspend`,
    `pre_suspend` and `post_suspend`) so that in between the appropriate update
    method can be called (`super().update(...)` for the serializer and
    `Case.objects.update(...) for the python API`).
    """

    @staticmethod
    def validate_for_suspend(case):
        if case.status != models.Case.STATUS_RUNNING:
            raise ValidationError("Only running cases can be suspended.")

    @staticmethod
    def pre_suspend(case, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_suspend_case",
            sender="pre_suspend_case",
            case=case,
            user=user,
            context=context,
        )

        validated_data["status"] = models.Case.STATUS_SUSPENDED

        for work_item in case.work_items.filter(status=models.WorkItem.STATUS_READY):
            api.suspend_work_item(work_item, user, context)

        return validated_data

    @staticmethod
    def post_suspend(case, user, context=None):
        send_event_with_deprecations(
            "post_suspend_case",
            sender="post_suspend_case",
            case=case,
            user=user,
            context=context,
        )

        return case


class ResumeCaseLogic:
    """
    Shared domain logic for resuming cases.

    Used in the `resumeCase` mutation and in the `resume_case` API. The logic
    for resuming a case is split in three parts (`validate_for_resume`,
    `pre_resume` and `post_resume`) so that in between the appropriate update
    method can be called (`super().update(...)` for the serializer and
    `Case.objects.update(...) for the python API`).
    """

    @staticmethod
    def validate_for_resume(case):
        if case.status != models.Case.STATUS_SUSPENDED:
            raise ValidationError("Only suspended cases can be resumed.")

    @staticmethod
    def pre_resume(case, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_resume_case",
            sender="pre_resume_case",
            case=case,
            user=user,
            context=context,
        )

        validated_data["status"] = models.Case.STATUS_RUNNING

        for work_item in case.work_items.filter(
            status=models.WorkItem.STATUS_SUSPENDED
        ):
            api.resume_work_item(work_item, user, context)

        return validated_data

    @staticmethod
    def post_resume(case, user, context=None):
        send_event_with_deprecations(
            "post_resume_case",
            sender="post_resume_case",
            case=case,
            user=user,
            context=context,
        )

        return case


class CancelWorkItemLogic:
    @staticmethod
    def validate_for_cancel(work_item):
        if work_item.status not in [
            models.WorkItem.STATUS_READY,
            models.WorkItem.STATUS_SUSPENDED,
        ]:
            raise ValidationError("Only ready or suspended work items can be canceled.")

    @staticmethod
    def pre_cancel(work_item, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_cancel_work_item",
            sender="pre_cancel_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        validated_data["status"] = models.WorkItem.STATUS_CANCELED
        validated_data["closed_at"] = timezone.now()
        validated_data["closed_by_user"] = user.username
        validated_data["closed_by_group"] = user.group

        if work_item.child_case and work_item.child_case.status in [
            models.Case.STATUS_RUNNING,
            models.Case.STATUS_SUSPENDED,
        ]:
            api.cancel_case(work_item.child_case, user, context)

        return validated_data

    @staticmethod
    def post_cancel(work_item, user, context=None):
        send_event_with_deprecations(
            "post_cancel_work_item",
            sender="post_cancel_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        return work_item


class SuspendWorkItemLogic:
    @staticmethod
    def validate_for_suspend(work_item):
        if work_item.status != models.WorkItem.STATUS_READY:
            raise ValidationError("Only ready work items can be suspended.")

    @staticmethod
    def pre_suspend(work_item, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_suspend_work_item",
            sender="pre_suspend_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        validated_data["status"] = models.WorkItem.STATUS_SUSPENDED

        if (
            work_item.child_case
            and work_item.child_case.status == models.Case.STATUS_RUNNING
        ):
            api.suspend_case(work_item.child_case, user, context)

        return validated_data

    @staticmethod
    def post_suspend(work_item, user, context=None):
        send_event_with_deprecations(
            "post_suspend_work_item",
            sender="post_suspend_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        return work_item


class ResumeWorkItemLogic:
    @staticmethod
    def validate_for_resume(work_item):
        if work_item.status != models.WorkItem.STATUS_SUSPENDED:
            raise ValidationError("Only suspended work items can be resumed.")

    @staticmethod
    def pre_resume(work_item, validated_data, user, context=None):
        send_event_with_deprecations(
            "pre_resume_work_item",
            sender="pre_resume_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        validated_data["status"] = models.WorkItem.STATUS_READY

        if (
            work_item.child_case
            and work_item.child_case.status == models.Case.STATUS_SUSPENDED
        ):
            api.resume_case(work_item.child_case, user, context)

        return validated_data

    @staticmethod
    def post_resume(work_item, user, context=None):
        send_event_with_deprecations(
            "post_resume_work_item",
            sender="post_resume_work_item",
            work_item=work_item,
            user=user,
            context=context,
        )

        return work_item
