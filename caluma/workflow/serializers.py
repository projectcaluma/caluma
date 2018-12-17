from django.db import transaction
from rest_framework import exceptions

from . import models, validators
from ..core import serializers
from ..form.models import Document
from .jexl import FlowJexl


class FlowJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(FlowJexl(), **kwargs)


class SaveWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "meta", "start", "form")


class ArchiveWorkflowSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Workflow


class PublishWorkflowSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save(update_fields=["is_published"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Workflow


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
        tasks = validated_data["tasks"]
        models.Flow.objects.filter(task_flows__task__in=tasks).delete()
        flow = models.Flow.objects.create(next=validated_data["next"])
        task_flows = [
            models.TaskFlow(task=task, workflow=instance, flow=flow) for task in tasks
        ]
        models.TaskFlow.objects.bulk_create(task_flows)

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
    class Meta:
        model = models.Task
        fields = ("slug", "name", "description", "type")


class ArchiveTaskSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.Task


class StartCaseSerializer(serializers.ModelSerializer):
    workflow = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.Workflow.objects.select_related("start")
    )
    parent_work_item = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.WorkItem.objects, required=False
    )

    @transaction.atomic
    def create(self, validated_data):
        workflow = validated_data["workflow"]
        validated_data["status"] = models.Case.STATUS_RUNNING
        validated_data["document"] = Document.objects.create(form_id=workflow.form_id)
        instance = super().create(validated_data)

        workflow = instance.workflow
        models.WorkItem.objects.create(
            case=instance, task=workflow.start, status=models.WorkItem.STATUS_READY
        )

        return instance

    class Meta:
        model = models.Case
        fields = ("workflow", "meta", "parent_work_item")


class CancelCaseSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    class Meta:
        model = models.Case
        fields = ("id",)

    def validate(self, data):
        if self.instance.status != models.Case.STATUS_RUNNING:
            raise exceptions.ValidationError("Only running cases can be canceled.")

        data["status"] = models.Case.STATUS_CANCELED
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.work_items.exclude(status=models.WorkItem.STATUS_COMPLETED).update(
            status=models.WorkItem.STATUS_CANCELED
        )
        return instance


class CompleteWorkItemSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        validators.WorkItemValidator().validate(
            status=self.instance.status,
            child_case=self.instance.child_case,
            task=self.instance.task,
            case=self.instance.case,
        )
        data["status"] = models.WorkItem.STATUS_COMPLETED
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        case = instance.case

        flow = models.Flow.objects.filter(task_flows__task=instance.task_id).first()
        flow_referenced_tasks = models.Task.objects.filter(task_flows__flow=flow)
        completed_flow_work_items = case.work_items.filter(
            task__in=flow_referenced_tasks
        ).exclude(status=models.WorkItem.STATUS_READY)

        if flow and flow_referenced_tasks.count() == completed_flow_work_items.count():
            jexl = FlowJexl()
            result = jexl.evaluate(flow.next)
            if not isinstance(result, list):
                result = [result]

            work_items = [
                models.WorkItem(
                    task_id=task, case=case, status=models.WorkItem.STATUS_READY
                )
                for task in result
            ]
            models.WorkItem.objects.bulk_create(work_items)
        else:
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETED
            case.save(update_fields=["status"])

        return instance

    class Meta:
        model = models.WorkItem
        fields = ("id",)
