from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.serializers import CharField, ListField
from simple_history.utils import bulk_create_with_history

from caluma.caluma_core.events import SendEventSerializerMixin

from ..caluma_core import serializers
from ..caluma_form.models import Document, Form
from . import events, models, validators
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


class FlowJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(FlowJexl(), **kwargs)


class GroupJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(GroupJexl(), **kwargs)


class SaveWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workflow
        fields = (
            "slug",
            "name",
            "description",
            "meta",
            "start_tasks",
            "allow_all_forms",
            "allow_forms",
            "is_archived",
            "is_published",
        )


class AddWorkflowFlowSerializer(serializers.ModelSerializer):
    workflow = serializers.GlobalIDField(source="slug")
    tasks = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Task.objects, many=True
    )
    next = FlowJexlField(required=True)

    def validate_next(self, value):
        jexl = FlowJexl()
        tasks = set(jexl.extract_tasks(value))

        if not tasks:
            raise exceptions.ValidationError(
                f"jexl `{value}` does not contain any tasks as return value"
            )

        available_tasks = set(
            models.Task.objects.filter(slug__in=tasks).values_list("slug", flat=True)
        )

        not_found_tasks = tasks - available_tasks
        if not_found_tasks:
            raise exceptions.ValidationError(
                f"jexl `{value}` contains invalid tasks [{', '.join(not_found_tasks)}]"
            )

        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context["request"].user
        tasks = validated_data["tasks"]
        models.Flow.objects.filter(task_flows__task__in=tasks).delete()
        flow = models.Flow.objects.create(
            next=validated_data["next"],
            created_by_user=user.username,
            created_by_group=user.group,
        )
        task_flows = [
            models.TaskFlow(task=task, workflow=instance, flow=flow) for task in tasks
        ]
        bulk_create_with_history(task_flows, models.TaskFlow)

        return instance

    class Meta:
        fields = ("workflow", "tasks", "next")
        model = models.Workflow


class RemoveFlowSerializer(serializers.ModelSerializer):
    flow = serializers.GlobalIDField(source="id")

    def update(self, instance, validated_data):
        models.Flow.objects.filter(pk=instance.pk).delete()
        return instance

    class Meta:
        fields = ("flow",)
        model = models.Flow


class SaveTaskSerializer(serializers.ModelSerializer):
    address_groups = GroupJexlField(
        required=False,
        allow_null=True,
        help_text=models.Task._meta.get_field("address_groups").help_text,
    )

    control_groups = GroupJexlField(
        required=False,
        allow_null=True,
        help_text=models.Task._meta.get_field("control_groups").help_text,
    )

    class Meta:
        model = models.Task
        fields = (
            "slug",
            "name",
            "description",
            "meta",
            "address_groups",
            "control_groups",
            "is_archived",
            "lead_time",
            "is_multiple_instance",
        )


class SaveSimpleTaskSerializer(SaveTaskSerializer):
    def validate(self, data):
        data["type"] = models.Task.TYPE_SIMPLE
        return super().validate(data)

    class Meta(SaveTaskSerializer.Meta):
        pass


class SaveCompleteWorkflowFormTaskSerializer(SaveTaskSerializer):
    def validate(self, data):
        data["type"] = models.Task.TYPE_COMPLETE_WORKFLOW_FORM
        return super().validate(data)

    class Meta(SaveTaskSerializer.Meta):
        pass


class SaveCompleteTaskFormTaskSerializer(SaveTaskSerializer):
    form = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=Form.objects, required=True
    )

    def validate(self, data):
        data["type"] = models.Task.TYPE_COMPLETE_TASK_FORM
        return super().validate(data)

    class Meta(SaveTaskSerializer.Meta):
        fields = SaveTaskSerializer.Meta.fields + ("form",)


class CaseSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    workflow = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Workflow.objects.prefetch_related("start_tasks")
    )
    parent_work_item = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.WorkItem.objects, required=False
    )
    form = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=Form.objects, required=False
    )

    def validate(self, data):
        form = data.get("form")
        workflow = data["workflow"]

        if form:
            if (
                not workflow.allow_all_forms
                and not workflow.allow_forms.filter(pk=form.pk).exists()
            ):
                raise exceptions.ValidationError(
                    f"Workflow {workflow.pk} does not allow to start case with form {form.pk}"
                )

        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
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

        instance = super().create(validated_data)

        # Django doesn't save reverse one-to-one relationships automatically:
        # https://code.djangoproject.com/ticket/18638
        if parent_work_item:
            parent_work_item.child_case = instance
            parent_work_item.save()

        workflow = instance.workflow
        tasks = workflow.start_tasks.all()

        work_items = bulk_create_work_items(tasks, instance, user)

        self.send_event(events.created_case, case=instance)
        for work_item in work_items:  # pragma: no cover
            self.send_event(events.created_work_item, work_item=work_item)

        return instance

    class Meta:
        model = models.Case
        fields = ("workflow", "meta", "parent_work_item", "form")


class SaveCaseSerializer(CaseSerializer):
    def create(self, validated_data):  # pragma: no cover
        instance = super().create(validated_data)
        self.send_event(events.created_case, case=instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.send_event(events.created_case, case=instance)
        return instance

    class Meta(CaseSerializer.Meta):
        fields = ("id", "workflow", "meta", "parent_work_item", "form")


class CancelCaseSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id",)

    def validate(self, data):
        if self.instance.status != models.Case.STATUS_RUNNING:
            raise exceptions.ValidationError("Only running cases can be canceled.")

        user = self.context["request"].user
        data["status"] = models.Case.STATUS_CANCELED
        data["closed_at"] = timezone.now()
        data["closed_by_user"] = user.username
        data["closed_by_group"] = user.group
        return super().validate(data)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        user = self.context["request"].user

        work_items = instance.work_items.exclude(
            status__in=[
                models.WorkItem.STATUS_COMPLETED,
                models.WorkItem.STATUS_CANCELED,
            ]
        )

        for work_item in work_items:
            work_item.status = models.WorkItem.STATUS_CANCELED
            work_item.closed_at = timezone.now()
            work_item.closed_by_user = user.username
            work_item.closed_by_group = user.group
            work_item.save()

        # send events in separate loop in order to be sure all operations are finished
        for work_item in work_items:
            self.send_event(events.cancelled_work_item, work_item=work_item)

        self.send_event(events.cancelled_case, case=instance)
        return instance


class CompleteWorkItemSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        user = self.context["request"].user
        validators.WorkItemValidator().validate(
            status=self.instance.status,
            child_case=self.instance.child_case,
            task=self.instance.task,
            case=self.instance.case,
            document=self.instance.document,
            info=self.context["info"],
        )
        data["status"] = models.WorkItem.STATUS_COMPLETED
        data["closed_at"] = timezone.now()
        data["closed_by_user"] = user.username
        data["closed_by_group"] = user.group
        return super().validate(data)

    def _can_continue(self, instance, task):
        # If a "multiple instance" task has running siblings, the task is not completed
        if task.is_multiple_instance:
            return not instance.case.work_items.filter(
                task=task, status=models.WorkItem.STATUS_READY
            ).exists()
        return instance.case.work_items.filter(
            task=task,
            status__in=(
                models.WorkItem.STATUS_COMPLETED,
                models.WorkItem.STATUS_SKIPPED,
            ),
        ).exists()

    @transaction.atomic
    def update(self, instance, validated_data):

        instance = super().update(instance, validated_data)
        user = self.context["request"].user
        case = instance.case

        if not self._can_continue(instance, instance.task):
            return instance

        flow = models.Flow.objects.filter(task_flows__task=instance.task_id).first()
        flow_referenced_tasks = models.Task.objects.filter(task_flows__flow=flow)

        all_complete = all(
            self._can_continue(instance, task) for task in flow_referenced_tasks
        )

        if flow and all_complete:
            jexl = FlowJexl()
            result = jexl.evaluate(flow.next)
            if not isinstance(result, list):
                result = [result]

            tasks = models.Task.objects.filter(pk__in=result)

            work_items = bulk_create_work_items(tasks, case, user, instance)

            for work_item in work_items:  # pragma: no cover
                self.send_event(events.created_work_item, work_item=work_item)
        else:
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETED
            case.closed_at = timezone.now()
            case.closed_by_user = user.username
            case.closed_by_group = user.group
            case.save()
            self.send_event(events.completed_case, case=case)

        self.send_event(events.completed_work_item, work_item=instance)

        return instance

    class Meta:
        model = models.WorkItem
        fields = ("id",)


class SkipWorkItemSerializer(CompleteWorkItemSerializer):
    def validate(self, data):
        if self.instance.status != models.WorkItem.STATUS_READY:
            raise exceptions.ValidationError("Only READY work items can be skipped")

        user = self.context["request"].user
        data["status"] = models.WorkItem.STATUS_SKIPPED
        data["closed_at"] = timezone.now()
        data["closed_by_user"] = user.username
        data["closed_by_group"] = user.group
        # We skip parent validation, as the work item is now "skipped",
        # meaning no other conditions need apply

        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.send_event(events.skipped_work_item, work_item=instance)
        return instance


class SaveWorkItemSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    work_item = serializers.GlobalIDField(source="id")
    name = CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=models.WorkItem._meta.get_field("name").help_text,
    )
    description = CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text=models.WorkItem._meta.get_field("description").help_text,
    )

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.send_event(events.created_work_item, work_item=instance)
        return instance

    class Meta:
        model = models.WorkItem
        fields = (
            "work_item",
            "name",
            "description",
            "assigned_users",
            "deadline",
            "meta",
        )


class CreateWorkItemSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    case = serializers.GlobalIDPrimaryKeyRelatedField(queryset=models.Case.objects)
    multiple_instance_task = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Task.objects, source="task"
    )
    controlling_groups = ListField(child=CharField(required=False), required=False)
    addressed_groups = ListField(child=CharField(required=False), required=False)
    name = CharField(
        required=False,
        allow_blank=True,
        help_text=models.WorkItem._meta.get_field("name").help_text,
    )
    description = CharField(
        required=False,
        allow_blank=True,
        help_text=models.WorkItem._meta.get_field("description").help_text,
    )

    def validate_multiple_instance_task(self, task):
        if not task.is_multiple_instance:
            raise exceptions.ValidationError(
                f"The given task type {task.type} does not allow creating multiple instances of it. Please set `isMultipleInstance` to true."
            )
        return task

    def validate(self, data):
        user = self.context["request"].user
        case = data["case"]
        task = data["task"]

        if not case.work_items.filter(
            task=task, status=models.WorkItem.STATUS_READY
        ).exists():
            raise exceptions.ValidationError(
                f"The given case {case.pk} does not have any running work items corresponding to the task {task.pk}. A new instance of a `MultipleInstanceTask` can only be created when there is at least one running sibling work item."
            )

        data["document"] = Document.objects.create_document_for_task(task, user)
        data["status"] = models.WorkItem.STATUS_READY

        if "controlling_groups" not in data:
            controlling_groups = get_jexl_groups(task.control_groups, case, user.group)
            if controlling_groups is not None:
                data["controlling_groups"] = controlling_groups

        if "addressed_groups" not in data:
            addressed_groups = get_jexl_groups(task.address_groups, case, user.group)
            if addressed_groups is not None:
                data["addressed_groups"] = addressed_groups

        return super().validate(data)

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.send_event(events.created_work_item, work_item=instance)
        return instance

    class Meta:
        model = models.WorkItem
        fields = (
            "case",
            "multiple_instance_task",
            "name",
            "description",
            "assigned_users",
            "addressed_groups",
            "controlling_groups",
            "deadline",
            "meta",
        )
