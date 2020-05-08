from django.core.exceptions import ValidationError

from ..caluma_form.validators import DocumentValidator
from . import models


class WorkItemValidator:
    def _validate_task_simple(self, task, case, document, user):
        pass

    def _validate_task_complete_workflow_form(self, task, case, document, user):
        self._validate_task_complete_task_form(task, case, case.document, user)

    def _validate_task_complete_task_form(self, task, case, document, user):
        DocumentValidator().validate(document, user)

    def validate(self, *, status, child_case, case, task, document, user, **kwargs):
        if status != models.WorkItem.STATUS_READY:
            raise ValidationError("Only ready work items can be completed.")

        if child_case:
            if child_case.status == models.Case.STATUS_RUNNING:
                raise ValidationError(
                    "Work item can only be completed when child case is in a finish state."
                )

        getattr(self, f"_validate_task_{task.type}")(task, case, document, user)
