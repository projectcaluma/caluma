from functools import partial

from django.contrib.postgres.fields import JSONField
from django.core import exceptions
from django.db import models
from localized_fields.fields import LocalizedField
from pyjexl import JEXL

from caluma.models import BaseModel

from ..jexl import ExtractTransformSubjectAnalyzer


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
        if self.is_archived or self.is_published:
            raise exceptions.ValidationError(
                f"Workflow {self.pk} may not be edited as it is archived or published"
            )

    def validate_flows(self):
        jexl = self.create_flow_jexl()
        added_task_specs = set(self.flows.values_list("task_specification", flat=True))

        errors = []
        for expr in self.flows.values_list("next", flat=True):
            task_specs = set(
                jexl.analyze(
                    expr,
                    partial(
                        ExtractTransformSubjectAnalyzer,
                        transforms=["taskSpecification"],
                    ),
                )
            )

            not_found_tasks = task_specs - added_task_specs
            if not_found_tasks:
                errors.append(
                    f"Task specifications `{', '.join(task_specs)}` specified in "
                    f"expression `{expr}` but only `{', '.join(added_task_specs)}` "
                    f"are available in workflow specification `{self.slug}`"
                )

        if errors:
            raise exceptions.ValidationError(errors)

    def create_flow_jexl(self):
        jexl = JEXL()
        jexl.add_transform("taskSpecification", lambda spec: spec)
        # TODO: add transforms e.g. answer
        return jexl

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
