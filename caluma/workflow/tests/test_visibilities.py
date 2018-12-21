import pytest

from .. import models
from ...form import models as form_models
from ...form.schema import Document
from ..schema import Case, WorkItem
from ..visibilities import AddressedGroups


@pytest.mark.parametrize(
    "work_item__addressed_groups,size", [(["unknown"], 0), (["admin", "other"], 1)]
)
def test_assigned_groups_work_item_visibility(db, admin_info, size, work_item):

    queryset = AddressedGroups().filter_queryset(
        WorkItem, models.WorkItem.objects, admin_info
    )
    assert queryset.count() == size


@pytest.mark.parametrize(
    "work_item__addressed_groups,size", [(["unknown"], 0), (["admin", "other"], 1)]
)
def test_assigned_groups_case_visibility(db, admin_info, size, work_item):

    queryset = AddressedGroups().filter_queryset(Case, models.Case.objects, admin_info)
    assert queryset.count() == size


@pytest.mark.parametrize(
    "work_item__addressed_groups,size", [(["unknown"], 0), (["admin", "other"], 1)]
)
def test_assigned_groups_document_visibility(db, admin_info, size, work_item):

    queryset = AddressedGroups().filter_queryset(
        Document, form_models.Document.objects, admin_info
    )
    assert queryset.count() == size
