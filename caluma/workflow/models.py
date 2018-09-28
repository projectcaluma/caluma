from django.contrib.postgres.fields import JSONField
from django.db import models
from localized_fields.fields import LocalizedField

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
        TaskSpecification, on_delete=models.CASCADE, related_name="+"
    )


class Flow(BaseModel):
    workflow_specification = models.ForeignKey(
        WorkflowSpecification, related_name="flows"
    )
    task_specification = models.ForeignKey(TaskSpecification, related_name="flows")
    next = models.TextField()

    class Meta:
        unique_together = ("workflow_specification", "task_specification")


class Workflow(BaseModel):
    STATUS_RUNNING = "running"
    STATUS_COMPLETE = "complete"

    STATUS_CHOICES = (STATUS_RUNNING, STATUS_COMPLETE)
    STATUS_CHOICE_TUPLE = (
        (STATUS_RUNNING, "Workflow is running and tasks need to be completed."),
        (STATUS_COMPLETE, "Workflow is done."),
    )

    workflow_specification = models.ForeignKey(
        WorkflowSpecification, related_name="workflows", on_delete=models.DO_NOTHING
    )
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})


class Task(BaseModel):
    STATUS_READY = "ready"
    STATUS_COMPLETE = "complete"

    STATUS_CHOICES = (STATUS_READY, STATUS_COMPLETE)
    STATUS_CHOICE_TUPLE = (
        (STATUS_READY, "Task is ready to be processed."),
        (STATUS_COMPLETE, "Task is done."),
    )

    task_specification = models.ForeignKey(
        TaskSpecification, on_delete=models.DO_NOTHING, related_name="tasks"
    )
    workflow = models.ForeignKey(
        Workflow, related_name="tasks", on_delete=models.CASCADE
    )
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})
