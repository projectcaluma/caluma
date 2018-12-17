from django.contrib.postgres.fields import JSONField
from django.db import models
from localized_fields.fields import LocalizedField

from ..core.models import SlugModel, UUIDModel


class Task(SlugModel):
    TYPE_SIMPLE = "simple"
    TYPE_COMPLETE_WORKFLOW_FORM = "complete_workflow_form"

    TYPE_CHOICES = (TYPE_SIMPLE, TYPE_COMPLETE_WORKFLOW_FORM)
    TYPE_CHOICES_TUPLE = (
        (TYPE_SIMPLE, "Task which can only be marked as completed."),
        (TYPE_COMPLETE_WORKFLOW_FORM, "Task completing defined workflow form."),
    )

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
    next = models.TextField()


class TaskFlow(UUIDModel):
    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, related_name="task_flows"
    )
    task = models.ForeignKey(Task, related_name="task_flows", on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, related_name="task_flows", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("workflow", "task")


class Case(UUIDModel):
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (STATUS_RUNNING, STATUS_COMPLETED, STATUS_CANCELED)
    STATUS_CHOICE_TUPLE = (
        (STATUS_RUNNING, "Case is running and work items need to be completed."),
        (STATUS_COMPLETED, "Case is done."),
        (STATUS_CANCELED, "Case is cancelled."),
    )

    workflow = models.ForeignKey(
        Workflow, related_name="cases", on_delete=models.DO_NOTHING
    )
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})
    document = models.OneToOneField(
        "form.Document",
        on_delete=models.PROTECT,
        related_name="case",
        blank=True,
        null=True,
    )


class WorkItem(UUIDModel):
    STATUS_READY = "ready"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (STATUS_READY, STATUS_COMPLETED, STATUS_CANCELED)
    STATUS_CHOICE_TUPLE = (
        (STATUS_READY, "Task is ready to be processed."),
        (STATUS_COMPLETED, "Task is done."),
        (STATUS_CANCELED, "Task is cancelled."),
    )

    task = models.ForeignKey(
        Task, on_delete=models.DO_NOTHING, related_name="work_items"
    )
    status = models.CharField(choices=STATUS_CHOICE_TUPLE, max_length=50, db_index=True)
    meta = JSONField(default={})

    case = models.ForeignKey(Case, related_name="work_items", on_delete=models.CASCADE)
    child_case = models.OneToOneField(
        Case,
        related_name="parent_work_item",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    """
    Defines case of a sub-workflow
    """
