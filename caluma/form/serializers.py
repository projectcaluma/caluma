from localized_fields.fields import LocalizedField
from pyjexl.jexl import JEXL
from rest_framework import exceptions, serializers

from . import models


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Form
        fields = ("slug", "name", "description", "meta")


class QuestionSerializer(serializers.ModelSerializer):
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
        fields = (
            "slug",
            "label",
            "type",
            "is_required",
            "is_hidden",
            "configuration",
            "meta",
        )


serializers.ModelSerializer.serializer_field_mapping.update(
    {LocalizedField: serializers.CharField}
)
