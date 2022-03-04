import graphene
from graphene import ConnectionField, String, relay
from graphene.types import ObjectType, generic
from graphene_django.rest_framework import serializer_converter

from ..caluma_core.filters import (
    CollectionFilterSetFactory,
    DjangoFilterSetConnectionField,
)
from ..caluma_core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..caluma_core.types import CountableConnectionBase, DjangoObjectType
from . import filters, models, serializers, simple_table


class AvailableField(ObjectType):
    """Available fields show users what can be selected in an analysis.

    The main identifier is the source path, but for display purposes,
    a label (field at current position) and a full_label (including
    parent fields' labels) is available.

    Frontends should query sub-fields (via prefix/depth) if is_leaf is
    False. Some fields can be non-leafs as well as values, such as
    dates: Dates can be extracted "as is", or we can extract a
    date part (such as year, quarter, ...) from it.
    """

    label = String()
    full_label = String()
    source_path = String()
    is_leaf = graphene.Boolean()
    is_value = graphene.Boolean()

    class Meta:
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase


class AvailableFieldConnection(CountableConnectionBase):
    class Meta:
        node = AvailableField


class AnalyticsCell(ObjectType):
    """A cell represents one value in the analytics output."""

    alias = String()
    value = String(required=False)


class AnalyticsRow(graphene.Connection):
    class Meta:
        node = AnalyticsCell


class AnalyticsTableContent(graphene.Connection):
    class Meta:
        node = AnalyticsRow


class AnalyticsOutput(ObjectType):
    records = ConnectionField(AnalyticsTableContent)

    @staticmethod
    def resolve_records(table, info, *args, **kwargs):
        rows = [
            AnalyticsRow(
                edges=[
                    {"node": {"alias": alias, "value": val}}
                    for alias, val in row.items()
                ]
            )
            for row in table.get_records()
        ]
        return rows


StartingObject = graphene.Enum(
    "StartingObject",
    [(key.upper(), key) for key, _ in models.AnalyticsTable.STARTING_OBJECT_CHOICES],
)

serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.StartingObjectField, lambda field: StartingObject
)


class AnalyticsTable(DjangoObjectType):
    available_fields = ConnectionField(
        AvailableFieldConnection,
        prefix=String(required=False),
        depth=graphene.Int(required=False),
    )
    result_data = graphene.Field(AnalyticsOutput)

    @staticmethod
    def resolve_available_fields(obj, info, prefix=None, depth=None, **kwargs):
        start = obj.get_starting_object(info)

        depth = depth if depth and depth > 0 else 1
        prefix = prefix.split(".") if prefix else []

        return sorted(
            [
                {
                    "id": ".".join(field.source_path()),
                    "label": field.label,
                    "full_label": field.full_label(),
                    "source_path": ".".join(field.source_path()),
                    "is_leaf": field.is_leaf(),
                    "is_value": field.is_value(),
                }
                for path, field in start.get_fields(prefix, depth).items()
            ],
            key=lambda field: field["id"],
        )

    @staticmethod
    def resolve_result_data(obj, info):
        return simple_table.SimpleTable(obj)

    class Meta:
        model = models.AnalyticsTable
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase


class AnalyticsField(DjangoObjectType):
    meta = generic.GenericScalar()
    filters = graphene.List(String, required=False)

    @classmethod
    def get_queryset(cls, queryset, info):
        return super().get_queryset(queryset, info).order_by("-created_at")

    class Meta:
        model = models.AnalyticsField
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase


class SaveAnalyticsTable(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveAnalyticsTableSerializer
        model_operations = ["create", "update"]


class RemoveAnalyticsTable(Mutation):
    class Meta:
        serializer_class = serializers.RemoveAnalyticsTableSerializer
        lookup_input_kwarg = "slug"
        model_operations = ["update"]


class SaveAnalyticsField(Mutation):
    class Meta:
        serializer_class = serializers.SaveAnalyticsFieldSerializer
        model_operations = ["create", "update"]


class RemoveAnalyticsField(Mutation):
    class Meta:
        serializer_class = serializers.RemoveAnalyticsFieldSerializer
        lookup_input_kwarg = "id"
        model_operations = ["update"]


class Mutation:
    save_analytics_table = SaveAnalyticsTable().Field()
    remove_analytics_table = RemoveAnalyticsTable().Field()

    save_analytics_field = SaveAnalyticsField().Field()
    remove_analytics_field = RemoveAnalyticsField().Field()


class Query:
    all_analytics_tables = DjangoFilterSetConnectionField(
        AnalyticsTable._meta.connection,
        filterset_class=CollectionFilterSetFactory(
            filters.AnalyticsTableFilterSet,
            orderset_class=filters.AnalyticsTableOrderSet,
        ),
    )
    analytics_table = graphene.Field(AnalyticsTable, slug=String(required=True))

    all_analytics_fields = DjangoFilterSetConnectionField(
        AnalyticsField._meta.connection,
        filterset_class=CollectionFilterSetFactory(filters.AnalyticsFieldFilterSet),
    )

    @staticmethod
    def resolve_analytics_table(_, info, slug):
        return models.AnalyticsTable.objects.get(pk=slug)
