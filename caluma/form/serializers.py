from rest_framework import serializers

from . import models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = "__all__"
