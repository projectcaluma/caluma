from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.constraints import UniqueConstraint
from localized_fields.fields import LocalizedField

from caluma.caluma_core.models import SlugModel, UUIDModel

from . import pivot_table, simple_table


class AnalyticsTable(SlugModel):
    STARTING_OBJECT_CHOICES = simple_table.BaseStartingObject.as_choices()

    meta = models.JSONField(default=dict)

    disable_visibilities = models.BooleanField(default=False)
    name = LocalizedField(blank=False, null=False, required=False)

    starting_object = models.CharField(max_length=250, choices=STARTING_OBJECT_CHOICES)

    def is_extraction(self):
        # We are an extraction table if there are ONLY
        # `FUNCTION_VALUE` type fields.
        return not self.fields.exclude(function=AnalyticsField.FUNCTION_VALUE).exists()

    def get_starting_object(self, info):
        return simple_table.BaseStartingObject.get_object(self.starting_object, info)

    def get_analytics(self, info):
        return (
            simple_table.SimpleTable(self, info)
            if self.is_extraction()
            else pivot_table.PivotTable(self, info)
        )

    def __repr__(self):
        return f"AnalyticsTable<{self.slug}>"


class AnalyticsField(UUIDModel):
    """Analytics field.

    May represent an aggregate (pivot) field on a pivot table, or
    an extraction field on an extraction table.

    The data_source references a field listed from the available fields
    that the starting object of the table provides.

    The function defines how the data of the
    specified source field is aggregated. While most of the functions
    are obvious by their name, the `FUNCTION_VALUE` is special: Those
    fields will not be aggregated, but the other aggregates will be
    grouped by this value.

    For example, if you define the following fields:
        - foo SUM
        - bar MIN
        - baz VALUE
    The output will contain one row for each unique value of `baz`.
    The sums and minimums calculated will all be in relation to rows with
    the same `baz` value.
    """

    FUNCTION_VALUE = "value"
    FUNCTION_SUM = "sum"
    FUNCTION_AVERAGE = "avg"
    FUNCTION_MAX = "max"
    FUNCTION_COUNT = "count"
    FUNCTION_MIN = "min"

    FUNCTION_CHOICES = [
        (FUNCTION_VALUE, "Plain value (Implies GROUP BY)"),
        (FUNCTION_SUM, "Sum"),
        (FUNCTION_COUNT, "Count"),
        (FUNCTION_AVERAGE, "Average (Mean)"),
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
        max_length=20, choices=FUNCTION_CHOICES, default=FUNCTION_VALUE
    )

    show_output = models.BooleanField(default=True)

    def __repr__(self):
        return f"AnalyticsField<{self.table.slug}.{self.alias}>"

    class Meta:
        constraints = [
            UniqueConstraint(
                name="unique_data_source",
                fields=["table", "data_source", "function"],
            ),
            UniqueConstraint(
                name="unique_alias",
                fields=["table", "alias"],
            ),
        ]
