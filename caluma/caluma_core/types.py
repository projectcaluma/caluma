from collections.abc import Iterable

import graphene
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from graphene.relay import PageInfo
from graphene.relay.connection import ConnectionField
from graphene_django import types
from graphene_django.fields import DjangoConnectionField
from graphene_django.utils import maybe_queryset
from graphql_relay import get_offset_with_default

from .pagination import connection_from_array, connection_from_array_slice


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

    TODO: properly implement max_limit, see
    https://github.com/graphql-python/graphene-django/blob/b552dcac24364d3ef824f865ba419c74605942b2/graphene_django/fields.py#L133
    """

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            # only query count on database when pagination is needed
            # resolve_connection may be removed again once following issue is fixed:
            # https://github.com/graphql-python/graphene-django/issues/177
            if all(args.get(x) is None for x in ["before", "after", "first", "last"]):
                _len = len(iterable)
            else:
                _len = iterable.count()
        else:  # pragma: no cover
            _len = len(iterable)

        # If after is higher than list_length, connection_from_array_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, _len)
        if max_limit is not None and "first" not in args:  # pragma: no cover
            args["first"] = max_limit

        connection = connection_from_array_slice(
            iterable[after:],
            args,
            slice_start=0,
            array_length=_len,
            array_slice_length=_len,
            connection_type=connection,
            edge_type=connection.Edge,
            page_info_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = _len
        return connection


class ConnectionField(ConnectionField):
    """
    Custom ConnectionField with fix for hasNextPage/hasPreviousPage.

    This can be removed, when (or better if)
    https://github.com/graphql-python/graphql-relay-py/issues/12
    is resolved.
    """

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if not resolved:
            resolved = []
        if isinstance(resolved, connection_type):  # pragma: no cover
            return resolved

        assert isinstance(resolved, Iterable), (
            "Resolved value from the connection field have to be iterable or instance of {0}. "
            'Received "{1}"'
        ).format(connection_type, resolved)
        connection = connection_from_array(
            resolved,
            args,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            page_info_type=PageInfo,
        )
        connection.iterable = resolved
        return connection
