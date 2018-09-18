import graphene
import pytest
from rest_framework.serializers import ChoiceField, Serializer

from .. import serializers


class SimpleSerializer(Serializer):
    choice = ChoiceField(choices=("test", "test description"))


@pytest.mark.parametrize(
    "field,result_type", [(SimpleSerializer().fields["choice"], graphene.String)]
)
def test_convert_serializer_field_to_enum(field, result_type):
    assert serializers.convert_serializer_field_to_enum(field) == result_type
