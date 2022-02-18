from django.core import exceptions
from django.db import transaction

from ..caluma_core import serializers
from . import models


class StartingObjectField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsTable.STARTING_OBJECT_CHOICES, **kwargs)


class TableTypeField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsTable.TABLE_TYPE_CHOICES, **kwargs)


class AggregateFunctionField(serializers.CalumaChoiceField):
    def __init__(self, **kwargs):
        super().__init__(models.AnalyticsTable.TABLE_TYPE_CHOICES, **kwargs)


class SaveAnalyticsTableSerializer(serializers.ModelSerializer):
    starting_object = StartingObjectField(required=False)
    table_type = TableTypeField(required=True)

    def validate(self, data):
        validated_data = super().validate(data)
        self._validate_type(validated_data)
        return validated_data

    def _validate_type(self, validated_data):
        table_type = validated_data.get("table_type", None)
        if table_type == models.AnalyticsTable.TYPE_EXTRACTION:
            self._validate_starting_object(validated_data)

    def _validate_starting_object(self, validated_data):
        # Schema is enforcing the value, but we have to enforce
        # it's set if the table is of extraction type
        if "starting_object" not in validated_data:
            raise exceptions.ValidationError(
                {
                    "startingObject": [
                        "starting object must be provided for tables with TYPE_EXTRACTION"
                    ]
                }
            )

    class Meta:
        model = models.AnalyticsTable
        fields = [
            "slug",
            "name",
            "starting_object",
            "table_type",
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
    function = AggregateFunctionField(required=False)

    def validate(self, data):
        validated_data = super().validate(data)
        self._validate_uniqueness(validated_data)

        table = validated_data["table"]

        if table.table_type == table.TYPE_EXTRACTION:
            self._validate_extraction_field_exists(validated_data)
        elif table.table_type == table.TYPE_PIVOT:
            self._validate_referenced_fields(validated_data)

        return validated_data

    def _validate_extraction_field_exists(self, data):
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

    def _validate_referenced_fields(self, validated_data):
        table = validated_data["table"]

        if not table.fields.filter(alias=validated_data["data_source"]).exists():
            source = validated_data["data_source"]
            raise exceptions.ValidationError(
                {
                    "dataSource": [
                        f"Pivot table field: Data source '{source}' must exist in base table"
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
            "function",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
        ]


class RemoveAnalyticsFieldSerializer(serializers.ModelSerializer):
    id = serializers.GlobalIDField()

    def validate(self, data):
        validated_data = super().validate(data)

        table = self.instance.table

        # if removing a field, we need to check if it's not
        # referenced by a followup table
        for follower in table.following_analytics_tables.all():
            if follower.fields.all().filter(data_source=self.instance.alias).exists():
                raise exceptions.ValidationError(
                    {
                        "dataSource": [
                            f"This field is still referenced in table {follower.slug}"
                        ]
                    }
                )

        return validated_data

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.delete()

        return instance

    class Meta:
        fields = ["id"]
        model = models.AnalyticsField
