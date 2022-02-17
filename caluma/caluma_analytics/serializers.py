from django.core import exceptions
from django.db import transaction

from ..caluma_core import serializers
from . import models


class StartingObjectField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsTable.STARTING_OBJECT_CHOICES, **kwargs)


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

    def validate(self, data):
        validated_data = super().validate(data)
        self._validate_uniqueness(validated_data)
        self._validate_field_exists(validated_data)
        return validated_data

    def _validate_field_exists(self, data):
        start = data["table"].get_starting_object(self.context["info"])
        data_source = data["data_source"]
        try:
            start.get_field(data_source.split("."))
        except KeyError:
            raise exceptions.ValidationError(
                {
                    "dataSource": [
                        f"Specified data source '{data_source}' is not available"
                    ]
                }
            )

    def _validate_uniqueness(self, data):
        existing_fields = data["table"].fields.all()
        if self.instance:
            existing_fields = existing_fields.exclude(pk=self.instance.pk)

        if existing_fields.filter(alias=data["alias"]).exists():
            raise exceptions.ValidationError(
                {"alias": ["Cannot use the same alias twice within the same table"]}
            )
        if existing_fields.filter(data_source=data["data_source"]).exists():
            raise exceptions.ValidationError(
                {
                    "dataSource": [
                        "Cannot use the same data source twice within the same table"
                    ]
                }
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
            "meta",
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
