from collections import Iterable

import graphene
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from graphene.relay import PageInfo
from graphene.relay.connection import ConnectionField
from graphene_django import types
from graphene_django.fields import DjangoConnectionField
from graphene_django.utils import maybe_queryset

from .pagination import connection_from_list, connection_from_list_slice


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
    """

    @classmethod
    def resolve_connection(cls, connection, args, iterable):
        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            # only query count on database when pagination is needed
            # resolve_connection may be removed again once following issue is fixed:
            # https://github.com/graphql-python/graphene-django/issues/177
            if "before" in args or "after" in args or "first" in args or "last" in args:
                _len = iterable.count()
            else:
                _len = len(iterable)
        else:  # pragma: no cover
            _len = len(iterable)
        connection = connection_from_list_slice(
            iterable,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
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
        if isinstance(resolved, connection_type):  # pragma: no cover
            return resolved

        assert isinstance(resolved, Iterable), (
            "Resolved value from the connection field have to be iterable or instance of {0}. "
            'Received "{1}"'
        ).format(connection_type, resolved)
        connection = connection_from_list(
            resolved,
            args,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = resolved
        return connection
