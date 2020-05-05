from django.db.models import Manager

from caluma.caluma_core.events import send_event

from ..caluma_form.models import Document
from . import events, models, utils


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

        work_items = utils.bulk_create_work_items(tasks, case, user)

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
