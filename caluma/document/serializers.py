from . import models
from .. import serializers


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("form", "meta")


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        fields = ("question", "meta", "document", "value")
