import pytest

from ..dynamic_tasks import BaseDynamicTasks, register_dynamic_task
from ..jexl import FlowJexl, GroupJexl


class CustomDynamicTasks(BaseDynamicTasks):
    @register_dynamic_task("dynamic-task")
    def resolve_dynamic_task(
        self, case, user, prev_work_item, context
    ):  # pragma: no cover
        return ["task-slug", "task-slug1", "task-slug2"]


@pytest.fixture
def task_config(db, task_factory):
    FlowJexl.dynamic_tasks_classes = [CustomDynamicTasks]

    for slug in ["task-slug", "task-slug1", "task-slug2"]:
        task_factory(slug=slug)


@pytest.mark.parametrize(
    "expression,expected_tasks",
    [
        (
            "63 > 62 ? 'test'|task : ['test2', 'test3']|tasks",
            {"test", "test2", "test3"},
        ),
        ("['test2', 'test3']|tasks", {"test2", "test3"}),
        ("'test'|task", {"test"}),
    ],
)
def test_flow_extract_tasks(expression, expected_tasks):
    jexl = FlowJexl()

    assert expected_tasks == set(jexl.extract_tasks(expression))


@pytest.mark.parametrize(
    "expression,expected_errors",
    [
        # correct tasks
        ("'task-slug'|task", []),
        ("['task-slug1', 'task-slug2', 'dynamic-task']|tasks", []),
        # invalid subject type
        ("100|task", ["`100` is not a valid task slug."]),
        ("'task-slug'|tasks", ["`task-slug` is not a valid list of tasks."]),
        # not existing tasks
        (
            "'some-task'|task",
            [
                "The task `some-task` does not exist or is not registered as dynamic task"
            ],
        ),
        (
            "['some-task', 'some-other-task']|tasks",
            [
                "The task `some-task` does not exist or is not registered as dynamic task",
                "The task `some-other-task` does not exist or is not registered as dynamic task",
            ],
        ),
    ],
)
def test_flow_jexl_validate(expression, expected_errors, task_config):
    errors = sorted(FlowJexl().validate(expression))

    assert sorted(expected_errors) == errors


@pytest.mark.parametrize(
    "expression,num_errors",
    [
        # correct cases
        ("['group1']|groups", 0),
        # invalid subject type
        ("100|groups", 1),
        ("'task-slug'|groups", 1),
    ],
)
def test_group_jexl_validate(expression, num_errors):
    jexl = GroupJexl()
    assert len(list(jexl.validate(expression))) == num_errors
