import pytest

from ...caluma_core.models import UUIDModel
from ...caluma_core.mutation import Mutation
from ...caluma_core.permissions import object_permission_for, permission_for
from ...caluma_core.serializers import ModelSerializer
from ...caluma_core.tests.fake_model import get_fake_model
from .. import permissions


@pytest.mark.parametrize(
    "info_fixture,is_authenticated", [("info", False), ("admin_info", True)]
)
def test_is_authenticated_permission(db, info_fixture, is_authenticated, request):
    info = request.getfixturevalue(info_fixture)
    assert (
        permissions.IsAuthenticated().has_permission(Mutation, info) == is_authenticated
    )


@pytest.mark.parametrize(
    "admin_groups,is_created_by", [(["admin_group"], True), (["nogroup"], False)]
)
def test_created_by_group_permission(db, admin_info, is_created_by, history_mock):
    FakeModel = get_fake_model(model_base=UUIDModel)
    instance = FakeModel.objects.create(created_by_group="admin_group")
    assert (
        permissions.CreatedByGroup().has_object_permission(
            Mutation, admin_info, instance
        )
        == is_created_by
    )


def test_is_authenticated_permission_super(db, request):
    FakeModel = get_fake_model()

    class Serializer(ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomPermission(permissions.IsAuthenticated):
        @permission_for(CustomMutation)
        def has_permission_for_custom_mutation(self, mutation, info):
            return False

    assert not CustomPermission().has_permission(
        CustomMutation, request.getfixturevalue("admin_info")
    )


@pytest.mark.parametrize("admin_groups", ["admin_group"])
def test_created_by_group_permission_super(db, admin_info, history_mock):
    FakeModel = get_fake_model(model_base=UUIDModel)
    instance = FakeModel.objects.create(created_by_group="admin_group")

    class Serializer(ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomPermission(permissions.CreatedByGroup):
        @object_permission_for(CustomMutation)
        def has_object_permission_for_custom_mutation(self, mutation, info, instance):
            return False

    assert not CustomPermission().has_object_permission(
        CustomMutation, admin_info, instance
    )
