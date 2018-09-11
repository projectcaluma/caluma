from rest_framework import serializers

from . import models


class WorkflowSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowSpecification
        fields = ("slug", "name", "description", "meta", "start")


class TaskSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskSpecification
        fields = ("slug", "name", "description", "type")
