from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import exceptions
from rest_framework.serializers import CharField, JSONField, ListField
from simple_history.utils import bulk_create_with_history

from caluma.caluma_core.events import SendEventSerializerMixin

from ..caluma_core import serializers
from ..caluma_form.models import Document, Form
from . import domain_logic, events, models, utils
from .jexl import FlowJexl, GroupJexl


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
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context["request"].user
        tasks = validated_data["tasks"]
        models.Flow.objects.filter(
            task_flows__workflow=instance, task_flows__task__in=tasks
        ).delete()
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
        try:
            data = domain_logic.StartCaseLogic.validate_for_start(data)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user

        context = validated_data.pop("context", {})
        validated_data = domain_logic.StartCaseLogic.pre_start(validated_data, user)

        case = super().create(validated_data)

        return domain_logic.StartCaseLogic.post_start(
            case, user, validated_data.get("parent_work_item"), context
        )

    class Meta:
        model = models.Case
        fields = ("workflow", "meta", "parent_work_item", "form")


class SaveCaseSerializer(CaseSerializer):
    context = JSONField(
        encoder=None,
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Provide extra context for DynamicGroups",
        style={"base_template": "textarea.html"},
    )

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.send_event(events.created_case, case=instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.send_event(events.created_case, case=instance)
        return instance

    class Meta(CaseSerializer.Meta):
        fields = ("id", "workflow", "meta", "parent_work_item", "form", "context")


class CancelCaseSerializer(SendEventSerializerMixin, serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id",)

    def validate(self, data):
        try:
            domain_logic.CancelCaseLogic.validate_for_cancel(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, instance, validated_data):
        user = self.context["request"].user

        super().update(
            instance, domain_logic.CancelCaseLogic.pre_cancel(validated_data, user)
        )

        domain_logic.CancelCaseLogic.post_cancel(instance, user)

        return instance


class CompleteWorkItemSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()
    context = JSONField(
        encoder=None,
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Provide extra context for DynamicGroups",
    )

    def validate(self, data):
        try:
            domain_logic.CompleteWorkItemLogic.validate_for_complete(
                self.instance, self.context["request"].user
            )
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, work_item, validated_data):
        user = self.context["request"].user

        context = validated_data.pop("context", {})
        validated_data = domain_logic.CompleteWorkItemLogic.pre_complete(
            validated_data, user
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.CompleteWorkItemLogic.post_complete(
            work_item, user, context
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")


class SkipWorkItemSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.SkipWorkItemLogic.validate_for_skip(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return data

    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.SkipWorkItemLogic.pre_skip(validated_data, user)

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.SkipWorkItemLogic.post_skip(work_item, user)

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id",)


class CancelWorkItemSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.CancelWorkItemLogic.validate_for_cancel(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return data

    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.CancelWorkItemLogic.pre_cancel(
            validated_data, user
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.CancelWorkItemLogic.post_cancel(work_item, user)

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id",)


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
            controlling_groups = utils.get_jexl_groups(
                task.control_groups, task, case, user
            )
            if controlling_groups is not None:
                data["controlling_groups"] = controlling_groups

        if "addressed_groups" not in data:
            addressed_groups = utils.get_jexl_groups(
                task.address_groups, task, case, user
            )
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
