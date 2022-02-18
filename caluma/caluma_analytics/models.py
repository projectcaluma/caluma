from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.constraints import UniqueConstraint
from localized_fields.fields import LocalizedField

from caluma.caluma_core.models import SlugModel, UUIDModel

from .simple_table import BaseStartingObject


class AnalyticsTable(SlugModel):
    STARTING_OBJECT_CHOICES = BaseStartingObject.as_choices()
    TYPE_EXTRACTION = "type_extraction"
    TYPE_PIVOT = "type_pivot"

    TABLE_TYPE_CHOICES = (
        (TYPE_EXTRACTION, "Data extraction"),
        (TYPE_PIVOT, "Pivot table"),
    )

    meta = models.JSONField(default=dict)

    table_type = models.CharField(max_length=250, choices=TABLE_TYPE_CHOICES, null=True)

    base_table = models.ForeignKey(
        "self",
        on_delete=models.RESTRICT,
        related_name="following_analytics_tables",
        null=True,
        default=None,
    )

    disable_visibilities = models.BooleanField(default=False)
    name = LocalizedField(blank=False, null=False, required=False)
    starting_object = models.CharField(
        max_length=250, choices=STARTING_OBJECT_CHOICES, null=True
    )

    def get_starting_object(self, info):
        return BaseStartingObject.get_object(self.starting_object, info)

    def __repr__(self):
        return f"AnalyticsTable<{self.slug}>"


class AnalyticsField(UUIDModel):
    """Analytics field.

    May represent an aggregate (pivot) field on a pivot table, or
    an extraction field on an extraction table.

    The data_source, in extraction fields, references a field
    listed from the available fields that the starting object of
    the table provides. In pivot tables, the data_source references
    a field of the base table, by its alias .

    The function (if it's a pivot field) defines how the data of the
    specified source field is aggregated. While most of the functions
    are obvious by their name, the `FUNCTION_GROUP` is special: Those
    fields will not be aggregated, but the other aggregates will be
    grouped by this value.
    For example, if you define the following fields:
        - foo SUM
        - bar MIN
        - baz GROUP
    The output will contain one row for each unique value of `baz`.
    The sums and minimums calculated will all be in relation to rows with
    the same `baz` value.
    """

    FUNCTION_GROUP = "group"
    FUNCTION_SUM = "sum"
    FUNCTION_AVERAGE = "avg"
    FUNCTION_MAX = "max"
    FUNCTION_MIN = "min"

    FUNCTION_CHOICES = [
        (FUNCTION_GROUP, "Group by"),
        (FUNCTION_SUM, "Sum"),
        (FUNCTION_AVERAGE, "Average"),
        (FUNCTION_MAX, "Max"),
        (FUNCTION_MIN, "Min"),
    ]

    alias = models.CharField(max_length=100)
    meta = models.JSONField(default=dict)

    data_source = models.TextField()
    table = models.ForeignKey(
        AnalyticsTable, on_delete=models.CASCADE, related_name="fields"
    )
    filters = ArrayField(models.TextField(), blank=True, null=True, default=list)
    function = models.CharField(
        max_length=20, choices=FUNCTION_CHOICES, null=True, default=None
    )

    def __repr__(self):
        return f"AnalyticsField<{self.table.slug}.{self.alias}>"

    class Meta:
        constraints = [
            UniqueConstraint(
                name="unique_data_source", fields=["table", "data_source"]
            ),
            UniqueConstraint(name="unique_alias", fields=["table", "alias"]),
        ]
