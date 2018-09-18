from django.contrib.postgres.fields import JSONField
from django.core import exceptions
from django.db import models
from localized_fields.fields import LocalizedField
from pyjexl import JEXL

from caluma.models import BaseModel, SlugModel


class TaskSpecification(SlugModel):
    TYPE_SIMPLE = "simple"

    TYPE_CHOICES = (TYPE_SIMPLE,)
    TYPE_CHOICES_TUPLE = ((TYPE_SIMPLE, "Task which can only be marked as completed."),)

    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=50)
    meta = JSONField(default={})
    is_archived = models.BooleanField(default=False)


class WorkflowSpecification(SlugModel):
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = JSONField(default={})
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    start = models.ForeignKey(
        TaskSpecification,
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )

    def validate_editable(self):
        if self.is_archived or self.is_published:
            raise exceptions.ValidationError(
                f"Workflow {self.pk} may not be edited as it is archived or published"
            )

    def create_flow_jexl(self):
        jexl = JEXL()
        jexl.add_transform("taskSpecification", lambda spec: spec)
        # TODO: add transforms e.g. answer
        return jexl


class Flow(BaseModel):
    workflow_specification = models.ForeignKey(
        WorkflowSpecification, related_name="flows"
    )
    task_specification = models.ForeignKey(TaskSpecification, related_name="flows")
    next = models.TextField()

    class Meta:
        unique_together = ("workflow_specification", "task_specification")
