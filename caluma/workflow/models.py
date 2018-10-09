from django.contrib.postgres.fields import JSONField
from django.db import models
from localized_fields.fields import LocalizedField

from caluma.models import SlugModel, UUIDModel


class Task(SlugModel):
    TYPE_SIMPLE = "simple"

    TYPE_CHOICES = (TYPE_SIMPLE,)
    TYPE_CHOICES_TUPLE = ((TYPE_SIMPLE, "Task which can only be marked as completed."),)

    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    type = models.CharField(choices=TYPE_CHOICES_TUPLE, max_length=50)
    meta = JSONField(default={})
    is_archived = models.BooleanField(default=False)


class Workflow(SlugModel):
    name = LocalizedField(blank=False, null=False, required=False)
    description = LocalizedField(blank=True, null=True, required=False)
    meta = JSONField(default={})
    is_published = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    start = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="+")
    form = models.ForeignKey(
        "form.Form",
        on_delete=models.DO_NOTHING,
        related_name="workflows",
        blank=True,
        null=True,
    )


class Flow(UUIDModel):
    workflow = models.ForeignKey(Workflow, related_name="flows")
    task = models.ForeignKey(Task, related_name="flows")
    next = models.TextField()

    class Meta:
        unique_together = ("workflow", "task")


class Case(UUIDModel):
    STATUS_RUNNING = "running"
    STATUS_COMPLETE = "complete"

    STATUS_CHOICES = (STATUS_RUNNING, STATUS_COMPLETE)
    STATUS_CHOICE_TUPLE = (
        (STATUS_RUNNING, "Case is running and work items need to be completed."),
        (STATUS_COMPLETE, "Case is done."),
    )

    workflow = models.ForeignKey(
        Workflow, related_name="cases", on_delete=models.DO_NOTHING
    )
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})
    document = models.ForeignKey(
        "form.Document",
        on_delete=models.DO_NOTHING,
        related_name="cases",
        blank=True,
        null=True,
    )


class WorkItem(UUIDModel):
    STATUS_READY = "ready"
    STATUS_COMPLETE = "complete"

    STATUS_CHOICES = (STATUS_READY, STATUS_COMPLETE)
    STATUS_CHOICE_TUPLE = (
        (STATUS_READY, "Task is ready to be processed."),
        (STATUS_COMPLETE, "Task is done."),
    )

    task = models.ForeignKey(
        Task, on_delete=models.DO_NOTHING, related_name="work_items"
    )
    case = models.ForeignKey(Case, related_name="work_items", on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})
