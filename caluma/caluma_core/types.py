from collections.abc import Iterable

import graphene
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.db.models.query_utils import DeferredAttribute
from graphene.relay import PageInfo
from graphene.relay.connection import ConnectionField
from graphene_django import types
from graphene_django.fields import DjangoConnectionField
from graphene_django.rest_framework import serializer_converter
from graphene_django.utils import maybe_queryset
from graphql_relay import cursor_to_offset, get_offset_with_default, offset_to_cursor

from .pagination import connection_from_array, connection_from_array_slice


def enum_type_from_field(
    name, field=None, choices=None, description=None, serializer_field=None
):
    """Create enum type for a given django model field.

    The model field must be of the right type (CharField) and
    have it's choices configured properly for this to work.

    Alternatively, you may pass a `choices` list of singular
    values (not CharField choices tuples!) as choices to use.

    Usually, you will want to pass the `serializer_field` parameter
    as well to register the type, so it will be correctly used in
    the appropriate places.

    Examples:
    >>> Field = enum_type_from_field("Field", field=MyModel.some_choice_field)
    Field

    >>> Field2 = enum_type_from_field("Field2", choices=["foo", "bar"])
    Field2

    """
    if field and isinstance(field, DeferredAttribute):
        field = field.field  # pragma: no cover
        choices = [(key.upper(), key) for key, _ in field.choices]
    else:
        # Force choices to be always uppercase
        choices = [(key.upper(), key) for key in choices]

    the_type = graphene.Enum(name, choices, description=description)

    if serializer_field:
        serializer_converter.get_graphene_type_from_serializer_field.register(
            serializer_field, lambda field: the_type
        )

    return the_type


class Node(object):
    """Base class to define queryset filters for all nodes."""

    # will be set in caluma_core.AppConfig.ready hook, see apps.py
    # to avoid recursive import error
    visibility_classes = None

    @classmethod
    def get_queryset(cls, queryset, info):
        if cls.visibility_classes is None:
            raise ImproperlyConfigured(
                "check that app `caluma.caluma_core` is part of your `INSTALLED_APPS` "
                "or custom node has `visibility_classes` properly assigned."
            )

        for visibility_class in cls.visibility_classes:
            queryset = visibility_class().filter_queryset(cls, queryset, info)

        return queryset.select_related()


class DjangoObjectType(Node, types.DjangoObjectType):
    """Django object type implementing default get_queryset with visibility layer."""

    class Meta:
        abstract = True


class CountableConnectionBase(graphene.Connection):
    """Connection subclass that supports totalCount."""

    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        try:
            # DjangoConnectionField sets the length already
            return self.length
        except AttributeError:
            if isinstance(self.iterable, QuerySet):  # pragma: no cover
                return self.iterable.count()
            return len(self.iterable)


class DjangoConnectionField(DjangoConnectionField):
    """
    Custom DjangoConnectionField with fix for hasNextPage/hasPreviousPage.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.

    WARNING: This is a one to one copy of the method in graphene django with the
    difference that we use our customized connection_from_array_slice function
    and that we only count on the database if pagination is actually used:
    https://github.com/graphql-python/graphene-django/blob/775644b5369bdc5fbb45d3535ae391a069ebf9d4/graphene_django/fields.py#L136
    """

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        # Remove the offset parameter and convert it to an after cursor.
        offset = args.pop("offset", None)
        after = args.get("after")
        if offset:
            if after:
                offset += cursor_to_offset(after) + 1
            # input offset starts at 1 while the graphene offset starts at 0
            args["after"] = offset_to_cursor(offset - 1)

        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            # only query count on database when pagination is needed
            # resolve_connection may be removed again once following issue is fixed:
            # https://github.com/graphql-python/graphene-django/issues/177
            if all(
                args.get(pagination_arg) is None
                for pagination_arg in ["before", "after", "first", "last"]
            ):
                list_length = len(iterable)
            else:
                list_length = iterable.count()
        else:  # pragma: no cover
            list_length = len(iterable)
        list_slice_length = (
            min(max_limit, list_length) if max_limit is not None else list_length
        )

        # If after is higher than list_length, connection_from_array_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        # This is commented out because we disable this functionality in our
        # settings explicitly.
        # if max_limit is not None and args.get("first", None) is None:
        #     if args.get("last", None) is not None:
        #         after = list_length - args["last"]
        #     else:
        #         args["first"] = max_limit

        connection = connection_from_array_slice(
            iterable[after:],
            args,
            slice_start=after,
            array_length=list_length,
            array_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            page_info_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection


class ConnectionField(ConnectionField):
    """
    Custom ConnectionField with fix for hasNextPage/hasPreviousPage.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.

    WARNING: This is a one to one copy of the method in graphene with the
    difference that we use our customized connection_from_array function:
    https://github.com/graphql-python/graphene/blob/61f0d8a8e09086fc74ad51d9ec80004674bd91f1/graphene/relay/connection.py#L146
    """

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):  # pragma: no cover
            return resolved

        assert isinstance(resolved, Iterable), (
            f"Resolved value from the connection field has to be an iterable or instance of {connection_type}. "
            f'Received "{resolved}"'
        )
        connection = connection_from_array(
            resolved,
            args,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            page_info_type=PageInfo,
        )
        connection.iterable = resolved
        return connection
