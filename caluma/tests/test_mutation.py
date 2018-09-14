import graphene
import pytest
from rest_framework import serializers

from .. import mutation


class SimpleSerializer(serializers.Serializer):
    choice = serializers.ChoiceField(choices=("test", "test description"))


@pytest.mark.parametrize(
    "field,result_type", [(SimpleSerializer().fields["choice"], graphene.String)]
)
def test_convert_serializer_field_to_enum(field, result_type):
    assert mutation.convert_serializer_field_to_enum(field) == result_type
