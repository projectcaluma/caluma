from django.db import transaction
from rest_framework import exceptions

from . import models
from .. import serializers
from .jexl import FlowJexl


class FlowJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(FlowJexl(), **kwargs)


class SaveWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workflow
        fields = ("slug", "name", "description", "meta", "start")


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
    task = serializers.GlobalIDPrimaryKeyRelatedField(queryset=models.Task.objects)
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

    def update(self, instance, validated_data):
        models.Flow.objects.update_or_create(
            workflow=instance,
            task=validated_data["task"],
            defaults={"next": validated_data["next"]},
        )

        return instance

    class Meta:
        fields = ("workflow", "task", "next")
        model = models.Workflow


class RemoveWorkflowFlowSerializer(serializers.ModelSerializer):
    workflow = serializers.GlobalIDField(source="slug")
    task = serializers.GlobalIDPrimaryKeyRelatedField(queryset=models.Task.objects)

    def update(self, instance, validated_data):
        task = validated_data["task"]
        models.Flow.objects.filter(task=task, workflow=instance).delete()

        return instance

    class Meta:
        fields = ("workflow", "task")
        model = models.Workflow


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

    @transaction.atomic
    def create(self, validated_data):
        validated_data["status"] = models.Case.STATUS_RUNNING
        instance = super().create(validated_data)

        workflow = instance.workflow

        models.WorkItem.objects.create(
            case=instance, task=workflow.start, status=models.WorkItem.STATUS_READY
        )

        return instance

    class Meta:
        model = models.Case
        fields = ("workflow", "meta")


class CompleteWorkItemSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        if self.instance.status == models.WorkItem.STATUS_COMPLETE:
            raise exceptions.ValidationError("Task has already been completed.")

        # TODO: add validation according to task type

        data["status"] = models.WorkItem.STATUS_COMPLETE
        return data

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        case = instance.case

        flow = models.Flow.objects.filter(
            workflow=case.workflow_id, task=instance.task_id
        ).first()

        if flow:
            jexl = FlowJexl()
            task = jexl.evaluate(flow.next)
            models.WorkItem.objects.create(
                task_id=task, case=case, status=models.WorkItem.STATUS_READY
            )
        else:
            # no more tasks, mark case as complete
            case.status = models.Case.STATUS_COMPLETE
            case.save(update_fields=["status"])

        return instance

    class Meta:
        model = models.WorkItem
        fields = ("id",)
