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

    def validate(self, data):
        instance = self.instance
        jexl = FlowJexl(instance)
        added_task_specs = set(
            instance.flows.values_list("task_specification", flat=True)
        )

        errors = []

        for expr in instance.flows.values_list("next", flat=True):
            task_specs = set(
                jexl.analyze(
                    expr,
                    partial(
                        ExtractTransformSubjectAnalyzer,
                        transforms=["taskSpecification"],
                    ),
                )
            )

            not_found_tasks = task_specs - added_task_specs
            if not_found_tasks:
                errors.append(
                    f"Task specifications `{', '.join(task_specs)}` specified in "
                    f"expression `{expr}` but only `{', '.join(added_task_specs)}` "
                    f"are available in workflow specification `{instance.slug}`"
                )

        if errors:
            raise exceptions.ValidationError(errors)

        return data

    class Meta:
        fields = ("id",)
        model = models.WorkflowSpecification


class AddWorkflowSpecificationFlowSerializer(serializers.ModelSerializer):
    workflow_specification = serializers.GlobalIDField(source="slug")
    task_specification = serializers.GlobalIDPrimaryKeyRelatedField(
        queryset=models.TaskSpecification.objects
    )
    next = FlowJexlField()

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
