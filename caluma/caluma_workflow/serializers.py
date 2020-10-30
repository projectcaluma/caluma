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


class ContextModelSerializer(serializers.ModelSerializer):
    context = JSONField(
        encoder=None,
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Provide extra context for dynamic jexl transforms and events",
    )

    def validate(self, data):
        self.context_data = data.pop("context", None)

        return super().validate(data)


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


class CaseSerializer(SendEventSerializerMixin, ContextModelSerializer):
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

        validated_data = domain_logic.StartCaseLogic.pre_start(validated_data, user)

        case = super().create(validated_data)

        return domain_logic.StartCaseLogic.post_start(
            case, user, validated_data.get("parent_work_item"), self.context_data
        )

    class Meta:
        model = models.Case
        fields = ("workflow", "meta", "parent_work_item", "form", "context")


class SaveCaseSerializer(CaseSerializer):
    @transaction.atomic
    def create(self, validated_data):
        self.send_event(
            events.pre_create_case, case=None, validated_data=validated_data
        )
        instance = super().create(validated_data)
        self.send_event(events.post_create_case, case=instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        self.send_event(
            events.pre_create_case, case=instance, validated_data=validated_data
        )
        instance = super().update(instance, validated_data)
        self.send_event(events.post_create_case, case=instance)
        return instance

    class Meta(CaseSerializer.Meta):
        fields = ("id", "workflow", "meta", "parent_work_item", "form", "context")


class CancelCaseSerializer(SendEventSerializerMixin, ContextModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id", "context")

    def validate(self, data):
        try:
            domain_logic.CancelCaseLogic.validate_for_cancel(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, case, validated_data):
        user = self.context["request"].user

        super().update(
            case,
            domain_logic.CancelCaseLogic.pre_cancel(
                case, validated_data, user, self.context_data
            ),
        )

        domain_logic.CancelCaseLogic.post_cancel(case, user, self.context_data)

        return case


class SuspendCaseSerializer(SendEventSerializerMixin, ContextModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id", "context")

    def validate(self, data):
        try:
            domain_logic.SuspendCaseLogic.validate_for_suspend(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, case, validated_data):
        user = self.context["request"].user

        super().update(
            case,
            domain_logic.SuspendCaseLogic.pre_suspend(
                case, validated_data, user, self.context_data
            ),
        )

        domain_logic.SuspendCaseLogic.post_suspend(case, user, self.context_data)

        return case


class ResumeCaseSerializer(SendEventSerializerMixin, ContextModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id", "context")

    def validate(self, data):
        try:
            domain_logic.ResumeCaseLogic.validate_for_resume(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, case, validated_data):
        user = self.context["request"].user

        super().update(
            case,
            domain_logic.ResumeCaseLogic.pre_resume(
                case, validated_data, user, self.context_data
            ),
        )

        domain_logic.ResumeCaseLogic.post_resume(case, user, self.context_data)

        return case


class CompleteWorkItemSerializer(ContextModelSerializer):
    id = serializers.GlobalIDField()

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

        validated_data = domain_logic.CompleteWorkItemLogic.pre_complete(
            work_item, validated_data, user, self.context_data
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.CompleteWorkItemLogic.post_complete(
            work_item, user, self.context_data
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")


class SkipWorkItemSerializer(ContextModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.SkipWorkItemLogic.validate_for_skip(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.SkipWorkItemLogic.pre_skip(
            work_item, validated_data, user, self.context_data
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.SkipWorkItemLogic.post_skip(
            work_item, user, self.context_data
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")


class CancelWorkItemSerializer(ContextModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.CancelWorkItemLogic.validate_for_cancel(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.CancelWorkItemLogic.pre_cancel(
            work_item, validated_data, user, self.context_data
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.CancelWorkItemLogic.post_cancel(
            work_item, user, self.context_data
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")


class SaveWorkItemSerializer(SendEventSerializerMixin, ContextModelSerializer):
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

    @transaction.atomic
    def update(self, instance, validated_data):
        self.send_event(
            events.pre_create_work_item,
            work_item=instance,
            validated_data=validated_data,
        )
        instance = super().update(instance, validated_data)
        self.send_event(events.post_create_work_item, work_item=instance)
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
            "context",
        )


class CreateWorkItemSerializer(SendEventSerializerMixin, ContextModelSerializer):
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
                task.control_groups, task, case, user, None, data.get("context", None)
            )
            if controlling_groups is not None:
                data["controlling_groups"] = sorted(controlling_groups)

        if "addressed_groups" not in data:
            addressed_groups = utils.get_jexl_groups(
                task.address_groups, task, case, user, None, data.get("context", None)
            )
            if addressed_groups is not None:
                data["addressed_groups"] = sorted(addressed_groups)

        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        self.send_event(
            events.pre_create_work_item, work_item=None, validated_data=validated_data
        )
        instance = super().create(validated_data)
        self.send_event(events.post_create_work_item, work_item=instance)
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
            "context",
        )


class SuspendWorkItemSerializer(ContextModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.SuspendWorkItemLogic.validate_for_suspend(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.SuspendWorkItemLogic.pre_suspend(
            work_item, validated_data, user, self.context_data
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.SuspendWorkItemLogic.post_suspend(
            work_item, user, self.context_data
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")


class ResumeWorkItemSerializer(ContextModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        try:
            domain_logic.ResumeWorkItemLogic.validate_for_resume(self.instance)
        except ValidationError as e:
            raise exceptions.ValidationError(str(e))

        return super().validate(data)

    @transaction.atomic
    def update(self, work_item, validated_data):
        user = self.context["request"].user

        validated_data = domain_logic.ResumeWorkItemLogic.pre_resume(
            work_item, validated_data, user, self.context_data
        )

        work_item = super().update(work_item, validated_data)
        work_item = domain_logic.ResumeWorkItemLogic.post_resume(
            work_item, user, self.context_data
        )

        return work_item

    class Meta:
        model = models.WorkItem
        fields = ("id", "context")
