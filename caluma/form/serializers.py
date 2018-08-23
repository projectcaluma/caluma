from pyjexl.jexl import JEXL
from rest_framework import exceptions, serializers

from . import models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = "__all__"
        read_only_fields = ("is_archived", "is_published")


class QuestionSerializer(serializers.ModelSerializer):
    is_required = serializers.CharField()
    is_hidden = serializers.CharField()

    def _validate_jexl_expression(self, expression):
        jexl = JEXL()
        # TODO: define transforms e.g. answer
        errors = list(jexl.validate(expression))
        if errors:
            raise exceptions.ValidationError(errors)

        return expression

    def validate_is_required(self, value):
        return self._validate_jexl_expression(value)

    def validate_is_hidden(self, value):
        return self._validate_jexl_expression(value)

    # TODO: validate configuration depending on type

    class Meta:
        model = models.Question
        fields = "__all__"
        read_only_fields = ("is_archived",)
