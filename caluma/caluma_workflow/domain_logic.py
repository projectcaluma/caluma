from django.core.exceptions import ValidationError

from caluma.caluma_core.events import send_event

from ..caluma_form.models import Document
from . import events, models, utils


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
