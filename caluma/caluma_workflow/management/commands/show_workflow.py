#!/usr/bin/python


from logging import getLogger

from django.core.management.base import BaseCommand
from django.db import transaction

from caluma.caluma_workflow.models import Task, Workflow

log = getLogger(__name__)


class Command(BaseCommand):
    """Dump workflow structure."""

    help = "Show workflow structure"

    def add_arguments(self, parser):

        parser.add_argument(
            dest="workflow",
            action="store",
            help="Slug of the workflow to show",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.workflow = Workflow.objects.get(pk=options["workflow"])
        self.visit(self.workflow)

    def _print(self, indent, data):
        ind_str = "   " * indent
        print(f"{ind_str}{data}")

    def visit(self, obj, indent=0):
        obj_type = str(type(obj).__name__)
        method_name = f"visit_{obj_type}"
        method = getattr(self, method_name)
        return method(obj, indent)

    def visit_Task(self, task, indent):
        taskflows = task.task_flows.filter(workflow=self.workflow)
        if taskflows.exists():
            next = taskflows.get().flow.next
        else:
            next = None

        self._print(
            indent,
            f"Task {task.slug} ({task.type})",
        )
        if task.type == Task.TYPE_COMPLETE_TASK_FORM:
            # other tasks *may* have a form, but it's not relevant
            self._print(indent + 1, f"Form: {task.form}")
        self._print(indent + 1, f"Next: {next}" if next else "(last task in sequence)")

    def visit_Workflow(self, workflow, indent):
        self._print(indent, f"Workflow {workflow.slug}")
        self._print(indent + 1, "Allowed forms:")
        for form in workflow.allow_forms.all():
            self.visit(form, indent + 2)

        start_tasks = workflow.start_tasks.all()
        self._print(indent + 1, "Start Tasks:")
        start_tasks = workflow.start_tasks.all()
        for task in start_tasks:
            self.visit(task, indent + 2)
        self._print(indent + 1, "Other Tasks:")

        other_tasks = (
            Task.objects.all()
            .exclude(pk__in=start_tasks)
            .filter(pk__in=workflow.task_flows.all().values("task"))
        )
        for task in other_tasks:
            self.visit(task, indent + 2)

    def visit_Form(self, form, indent):
        self._print(indent, f"Form: {form.slug}")
