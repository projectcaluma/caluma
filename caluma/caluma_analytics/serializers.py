from django.core import exceptions
from django.db import transaction

from ..caluma_core import serializers
from . import models


class StartingObjectField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsTable.STARTING_OBJECT_CHOICES, **kwargs)


class AggregateFunctionField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsField.FUNCTION_CHOICES, **kwargs)


class SaveAnalyticsTableSerializer(serializers.ModelSerializer):
    starting_object = StartingObjectField(required=True)

    class Meta:
        model = models.AnalyticsTable
        fields = [
            "slug",
            "name",
            "starting_object",
            "created_at",
            "modified_at",
            "disable_visibilities",
            "meta",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
        ]


class RemoveAnalyticsTableSerializer(serializers.ModelSerializer):
    slug = serializers.GlobalIDField()

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.delete()
        return instance

    class Meta:
        lookup_input_kwarg = "slug"
        fields = ["slug"]
        model = models.AnalyticsTable


class SaveAnalyticsFieldSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField(required=False)
    function = AggregateFunctionField(required=True)

    def validate(self, data):
        validated_data = super().validate(data)

        self._validate_extraction_field(validated_data)

        return validated_data

    def _validate_extraction_field(self, data):
        start = data["table"].get_starting_object(self.context["info"])
        data_source = data["data_source"]
        try:
            field = start.get_field(data_source.split("."))
        except KeyError:
            raise exceptions.ValidationError(
                {
                    "dataSource": [
                        f"Specified data source '{data_source}' is not available"
                    ]
                }
            )
        if not field.is_value():
            raise exceptions.ValidationError(
                {
                    "dataSource": [
                        f"Specified data source '{data_source}' is "
                        "not a value field. Select a subfield."
                    ]
                }
            )
        function = data["function"].upper()
        if function not in field.supported_functions():
            raise exceptions.ValidationError(
                {"function": [f"Function '{function}' is not supported on this field"]}
            )

    class Meta:
        model = models.AnalyticsField
        fields = [
            "id",
            "alias",
            "table",
            "data_source",
            "created_at",
            "modified_at",
            "filters",
            "show_output",
            "meta",
            "function",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
        ]


class RemoveAnalyticsFieldSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.delete()

        return instance

    class Meta:
        fields = ["id"]
        model = models.AnalyticsField
