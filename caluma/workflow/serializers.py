from functools import partial

from rest_framework import exceptions

from . import models
from .. import serializers
from ..jexl import ExtractTransformSubjectAnalyzer
from .jexl import FlowJexl


class FlowJexlField(serializers.JexlField):
    def __init__(self, **kwargs):
        super().__init__(FlowJexl(), **kwargs)


class SaveWorkflowSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "meta", "start")


class ArchiveWorkflowSpecificationSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.WorkflowSpecification


class PublishWorkflowSpecificationSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_published = True
        instance.save(update_fields=["is_published"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.WorkflowSpecification


class AddWorkflowSpecificationFlowSerializer(serializers.ModelSerializer):
    workflow_specification = serializers.GlobalIDField(source="slug")
    task_specification = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.TaskSpecification.objects
    )
    next = FlowJexlField(required=True)

    def validate_next(self, value):
        jexl = FlowJexl()

        task_specs = set(
            jexl.analyze(
                value,
                partial(
                    ExtractTransformSubjectAnalyzer, transforms=["taskSpecification"]
                ),
            )
        )

        if not task_specs:
            raise exceptions.ValidationError(
                f"jexl `{value}` does not contain any task specification as return value"
            )

        available_task_specs = set(
            models.TaskSpecification.objects.filter(slug__in=task_specs).values_list(
                "slug", flat=True
            )
        )

        not_found_task_specs = task_specs - available_task_specs
        if not_found_task_specs:
            raise exceptions.ValidationError(
                f"jexl `{value}` contains invalid task specification: "
                f"[{', '.join(not_found_task_specs)}]"
            )

        return value

    def update(self, instance, validated_data):
        models.Flow.objects.update_or_create(
            workflow_specification=instance,
            task_specification=validated_data["task_specification"],
            defaults={"next": validated_data["next"]},
        )

        return instance

    class Meta:
        fields = ("workflow_specification", "task_specification", "next")
        model = models.WorkflowSpecification


class RemoveWorkflowSpecificationFlowSerializer(serializers.ModelSerializer):
    workflow_specification = serializers.GlobalIDField(source="slug")
    task_specification = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.TaskSpecification.objects
    )

    def update(self, instance, validated_data):
        task_specification = validated_data["task_specification"]
        models.Flow.objects.filter(
            task_specification=task_specification, workflow_specification=instance
        ).delete()

        return instance

    class Meta:
        fields = ("workflow_specification", "task_specification")
        model = models.WorkflowSpecification


class SaveTaskSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskSpecification
        fields = ("slug", "name", "description", "type")


class ArchiveTaskSpecificationSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(source="slug")

    def update(self, instance, validated_data):
        instance.is_archived = True
        instance.save(update_fields=["is_archived"])
        return instance

    class Meta:
        fields = ("id",)
        model = models.TaskSpecification
