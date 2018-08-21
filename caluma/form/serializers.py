from pyjexl.jexl import JEXL
from rest_framework import exceptions, serializers

from . import models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    is_required = serializers.CharField()
    is_hidden = serializers.CharField()

    def validate_is_required(self, value):
        jexl = JEXL()
        # TODO: define transforms e.g. answer
        errors = list(jexl.validate(value))
        if errors:
            raise exceptions.ValidationError(errors)

        return value

    def validate_is_hidden(self, value):
        return self.validate_is_required(value)

    # TODO: validate configuration depending on type

    class Meta:
        model = models.Question
        fields = "__all__"
