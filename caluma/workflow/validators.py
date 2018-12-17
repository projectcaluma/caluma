from rest_framework import exceptions

from . import models
from ..form.validators import DocumentValidator


class WorkItemValidator:
    def _validate_task_simple(self, task, document):
        pass

    def _validate_task_complete_workflow_form(self, task, document):
        DocumentValidator().validate(answers=document.answers, form=document.form)

    def validate(self, *, status, child_case, case, task, **kwargs):
        if status != models.WorkItem.STATUS_READY:
            raise exceptions.ValidationError("Only ready work items can be completed.")

        if child_case:
            if child_case.status == models.Case.STATUS_RUNNING:
                raise exceptions.ValidationError(
                    "Work item can only be completed when child case is in a finish state."
                )

        getattr(self, f"_validate_task_{task.type}")(task, case.document)
