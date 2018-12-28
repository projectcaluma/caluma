import pytest

from ..jexl import FlowJexl, GroupJexl


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
    "expression,num_errors",
    [
        # correct cases
        ('"task-slug"|task', 0),
        ('["task-slug1", "task-slug2"]|tasks', 0),
        # invalid subject type
        ("100|task", 1),
        ("'task-slug'|tasks", 1),
    ],
)
def test_flow_jexl_validate(expression, num_errors):
    jexl = FlowJexl()
    assert len(list(jexl.validate(expression))) == num_errors


@pytest.mark.parametrize(
    "expression,num_errors",
    [
        # correct cases
        ('["group1"]|groups', 0),
        # invalid subject type
        ("100|groups", 1),
        ("'task-slug'|groups", 1),
    ],
)
def test_group_jexl_validate(expression, num_errors):
    jexl = GroupJexl()
    assert len(list(jexl.validate(expression))) == num_errors
