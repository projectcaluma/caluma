import pytest
from django.core.exceptions import ValidationError

from caluma.caluma_workflow.dynamic_tasks import BaseDynamicTasks, register_dynamic_task
from caluma.caluma_workflow.jexl import FlowJexl


class CustomDynamicTasks(BaseDynamicTasks):
    @register_dynamic_task("task-1")
    def resolve_task_1(self, case, user, prev_work_item, context):
        return "some-task"

    @register_dynamic_task("task-2")
    def resolve_task_2(self, case, user, prev_work_item, context):
        return ["some-task", "some-other-task"]


@pytest.mark.parametrize(
    "expression,success,expected_result",
    [
        ('"task-1"|task', True, "some-task"),
        ('["task-1"]|tasks', True, ["some-task"]),
        ('["task-2"]|tasks', True, ["some-task", "some-other-task"]),
        ('["task-1", "task-2"]|tasks', True, ["some-task", "some-other-task"]),
        # task transform can only return single values
        ('"task-2"|task', False, None),
    ],
)
def test_dynamic_tasks(
    db, case, admin_user, work_item, expression, success, expected_result
):
    FlowJexl.dynamic_tasks_classes = [CustomDynamicTasks]

    jexl = FlowJexl(case, admin_user, work_item, {})

    if success:
        assert sorted(jexl.evaluate(expression)) == sorted(expected_result)
    else:
        with pytest.raises(ValidationError) as error:
            jexl.evaluate(expression)

        assert (
            "The dynamic task `task-2` used by the `task` transform should not return more than one task -- it returned 2"
            in str(error.value)
        )
