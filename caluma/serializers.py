from graphql_relay import from_global_id, to_global_id
from rest_framework import relations, serializers


class GlobalIDPrimaryKeyRelatedField(relations.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        _, data = from_global_id(data)
        return super().to_internal_value(data)

    def to_representation(self, value):
        value = super().to_representation(value)
        return to_global_id(self.get_queryset().model.__name__, value)


class ModelSerializer(serializers.ModelSerializer):
    serializer_related_field = GlobalIDPrimaryKeyRelatedField
