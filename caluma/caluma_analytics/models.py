from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.constraints import UniqueConstraint
from localized_fields.fields import LocalizedField

from caluma.caluma_core.models import SlugModel, UUIDModel

from .simple_table import BaseStartingObject


class AnalyticsTable(SlugModel):
    STARTING_OBJECT_CHOICES = BaseStartingObject.as_choices()

    meta = models.JSONField(default=dict)

    disable_visibilities = models.BooleanField(default=False)
    name = LocalizedField(blank=False, null=False, required=False)
    starting_object = models.CharField(max_length=250, choices=STARTING_OBJECT_CHOICES)

    def get_starting_object(self, info):
        return BaseStartingObject.get_object(self.starting_object, info)


class AnalyticsField(UUIDModel):
    alias = models.CharField(max_length=100)
    meta = models.JSONField(default=dict)

    data_source = models.TextField()
    table = models.ForeignKey(
        AnalyticsTable, on_delete=models.CASCADE, related_name="fields"
    )
    filters = ArrayField(models.TextField(), blank=True, null=True, default=list)

    class Meta:
        constraints = [
            UniqueConstraint(
                name="unique_data_source", fields=["table", "data_source"]
            ),
            UniqueConstraint(name="unique_alias", fields=["table", "alias"]),
        ]
