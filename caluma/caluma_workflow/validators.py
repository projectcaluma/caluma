from django.core.exceptions import ValidationError

from ..caluma_form.validators import DocumentValidator
from . import models


class WorkItemValidator:
    def _validate_task_simple(self, task, case, document, user, **kwargs):
        pass

    def _validate_task_complete_workflow_form(
        self, task, case, document, user, **kwargs
    ):
        self._validate_task_complete_task_form(
            task, case, case.document, user, **kwargs
        )

    def _validate_task_complete_task_form(
        self,
        task,
        case,
        document,
        user,
        validation_context=None,
        data_source_context=None,
        **kwargs,
    ):
        DocumentValidator().validate(
            document,
            user,
            validation_context=validation_context,
            data_source_context=data_source_context,
            **kwargs,
        )

    def validate(
        self,
        *,
        status,
        child_case,
        case,
        task,
        document,
        user,
        validation_context=None,
        data_source_context=None,
        **kwargs,
    ):
        if case.status != models.Case.STATUS_RUNNING:
            raise ValidationError("Only work items of running cases can be completed.")

        if status != models.WorkItem.STATUS_READY:
            raise ValidationError("Only ready work items can be completed.")

        if child_case:
            if child_case.status == models.Case.STATUS_RUNNING:
                raise ValidationError(
                    "Work item can only be completed when child case is in a finish state."
                )

        getattr(self, f"_validate_task_{task.type}")(
            task,
            case,
            document,
            user,
            validation_context=validation_context,
            data_source_context=data_source_context,
            **kwargs,
        )
