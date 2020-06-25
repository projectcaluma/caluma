import pytest

from caluma.caluma_workflow.dynamic_groups import (
    BaseDynamicGroups,
    register_dynamic_group,
)
from caluma.caluma_workflow.jexl import GroupJexl


class CustomDynamicGroups(BaseDynamicGroups):
    @register_dynamic_group("admin")
    def resolve_admin(self, task, case, user, prev_work_item):
        return "admin-group-slug"

    @register_dynamic_group("staff")
    def resolve_staff(self, task, case, user, prev_work_item):
        return ["staff-a", "staff-b"]


@pytest.mark.parametrize("case__created_by_group", ["group1"])
@pytest.mark.parametrize(
    "expression,expected_result",
    [
        ('["admin"]|groups', ["admin-group-slug"]),
        ('["staff"]|groups', ["staff-a", "staff-b"]),
        ('["admin", "staff"]|groups', ["admin-group-slug", "staff-a", "staff-b"]),
        ('["some-other-group"]|groups', ["some-other-group"]),
    ],
)
def test_dynamic_groups(
    db, task, case, admin_user, work_item, expression, expected_result
):
    GroupJexl.dynamic_groups_classes = [CustomDynamicGroups]

    jexl = GroupJexl(None, task, case, admin_user, work_item)

    assert sorted(jexl.evaluate(expression)) == sorted(expected_result)
