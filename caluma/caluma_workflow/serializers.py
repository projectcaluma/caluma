import itertools

from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions
from simple_history.utils import bulk_create_with_history

from ..caluma_core import serializers
from ..caluma_form.models import Document, Form
from . import models, validators
from .jexl import FlowJexl, GroupJexl


def evaluate_assigned_groups(task):
    if task.address_groups:
        return GroupJexl().evaluate(task.address_groups)

    return []


def get_addressed_groups(task):
    addressed_groups = [evaluate_assigned_groups(task)]
    if task.is_multiple_instance:
        addressed_groups = [[x] for x in addressed_groups[0]]
    return addressed_groups


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

    class Meta:
        model = models.Task
        fields = (
            "slug",
            "name",
            "description",
            "meta",
            "address_groups",
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


class CaseSerializer(serializers.ModelSerializer):
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

        instance = super().create(validated_data)
        if parent_work_item:
            parent_work_item.child_case = instance
            parent_work_item.save()

        workflow = instance.workflow
        tasks = workflow.start_tasks.all()

        work_items = itertools.chain(
            *[
                [
                    models.WorkItem(
                        addressed_groups=groups,
                        task_id=task.pk,
                        deadline=task.calculate_deadline(),
                        document=Document.objects.create_document_for_task(task, user),
                        case=instance,
                        status=models.WorkItem.STATUS_READY,
                        created_by_user=user.username,
                        created_by_group=user.group,
                    )
                    for groups in get_addressed_groups(task)
                ]
                for task in tasks
            ]
        )

        bulk_create_with_history(work_items, models.WorkItem)
        return instance

    class Meta:
        model = models.Case
        fields = ("workflow", "meta", "parent_work_item", "form")


class SaveCaseSerializer(CaseSerializer):
    class Meta(CaseSerializer.Meta):
        fields = ("id", "workflow", "meta", "parent_work_item", "form")


class CancelCaseSerializer(serializers.ModelSerializer):
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
        instance.work_items.exclude(
            status__in=[
                models.WorkItem.STATUS_COMPLETED,
                models.WorkItem.STATUS_CANCELED,
            ]
        ).update(
            status=models.WorkItem.STATUS_CANCELED,
            closed_at=timezone.now(),
            closed_by_user=user.username,
            closed_by_group=user.group,
        )
        return instance


class CompleteWorkItemSerializer(serializers.ModelSerializer):
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

            work_items = itertools.chain(
                *[
                    [
                        models.WorkItem(
                            addressed_groups=groups,
                            task_id=task.pk,
                            deadline=task.calculate_deadline(),
                            document=Document.objects.create_document_for_task(
                                task, user
                            ),
                            case=case,
                            status=models.WorkItem.STATUS_READY,
                            created_by_user=user.username,
                            created_by_group=user.group,
                        )
                        for groups in get_addressed_groups(task)
                    ]
                    for task in tasks
                ]
            )

            bulk_create_with_history(work_items, models.WorkItem)
        else:
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETED
            case.closed_at = timezone.now()
            case.closed_by_user = user.username
            case.closed_by_group = user.group
            case.save()

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


class SaveWorkItemSerializer(serializers.ModelSerializer):
    work_item = serializers.GlobalIDField(source="id")

    class Meta:
        model = models.WorkItem
        fields = ("work_item", "assigned_users", "deadline", "meta")


class CreateWorkItemSerializer(serializers.ModelSerializer):
    case = serializers.GlobalIDPrimaryKeyRelatedField(queryset=models.Case.objects)
    multiple_instance_task = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Task.objects, source="task"
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
        return super().validate(data)

    class Meta:
        model = models.WorkItem
        fields = (
            "case",
            "multiple_instance_task",
            "assigned_users",
            "addressed_groups",
            "deadline",
            "meta",
        )
