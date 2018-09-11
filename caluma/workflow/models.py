from django.contrib.postgres.fields import JSONField
from django.db import models
from graphql.error import GraphQLError
from localized_fields.fields import LocalizedField

from caluma.models import BaseModel


class TaskSpecification(BaseModel):
    TYPE_SIMPLE = "simple"

    TYPE_CHOICES = (TYPE_SIMPLE,)
    TYPE_CHOICES_TUPLE = ((type_choice, type_choice) for type_choice in TYPE_CHOICES)

    slug = models.SlugField(max_length=50, primary_key=True)
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=50)
    meta = JSONField(default={})
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.slug


class WorkflowSpecification(BaseModel):
    slug = models.SlugField(max_length=50, primary_key=True)
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = JSONField(default={})
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    start = models.ForeignKey(
        TaskSpecification, on_delete=models.CASCADE, related_name="+"
    )

    def validate_editable(self):
        # TODO: Think of a more generic way to be implemented in graphene
        # https://github.com/graphql-python/graphene/issues/777
        if self.is_archived or self.is_published:
            raise GraphQLError(
                f"Workflow {self.pk} may not be edited as it is archived or published"
            )

    def __str__(self):
        return self.slug


class Flow(BaseModel):
    workflow_specification = models.ForeignKey(
        WorkflowSpecification, related_name="flows"
    )
    task_specification = models.ForeignKey(TaskSpecification, related_name="flows")
    next = models.TextField()

    class Meta:
        unique_together = ("workflow_specification", "task_specification")
