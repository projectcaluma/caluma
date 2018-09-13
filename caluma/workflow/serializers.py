from rest_framework import serializers

from . import models


class WorkflowSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "meta")


class TaskSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskSpecification
        fields = ("slug", "name", "description", "type")
