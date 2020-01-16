import pytest

from ...caluma_form import models as form_models
from ...caluma_form.schema import Answer, Document
from .. import models
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


@pytest.mark.parametrize(
    "work_item__addressed_groups,size", [(["unknown"], 0), (["admin", "other"], 1)]
)
def test_assigned_groups_answer_visibility(db, admin_info, size, work_item, answer):

    queryset = AddressedGroups().filter_queryset(
        Answer, form_models.Answer.objects, admin_info
    )
    assert queryset.count() == size
