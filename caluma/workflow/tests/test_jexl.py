import pytest

from ..jexl import FlowJexl


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
