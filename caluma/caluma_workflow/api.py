from typing import Optional

from caluma.caluma_form.models import Form
from caluma.caluma_user.models import BaseUser

from . import domain_logic, models


def start_case(
    workflow: models.Workflow,
    user: BaseUser,
    form: Optional[Form] = None,
    parent_work_item: Optional[models.WorkItem] = None,
    **kwargs
) -> models.Case:
    """
    Start a case of a given workflow (just like `saveCase`).

    Similar to Case.objects.create(), but with the same business logic as
    used in the `saveCase` mutation.

    Usage example:
    ```py
    start_case(
        workflow=Workflow.objects.get(pk="my-wf"),
        form=Form.objects.get(pk="my-form")),
        user=AnonymousUser()
    )
    ```
    """
    data = {"workflow": workflow, "form": form, "parent_work_item": parent_work_item}

    data.update(kwargs)

    validated_data = domain_logic.StartCaseLogic.pre_start(
        domain_logic.StartCaseLogic.validate_for_start(data), user
    )

    case = models.Case.objects.create(**validated_data)

    return domain_logic.StartCaseLogic.post_start(case, user, parent_work_item)
