import graphene
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from graphene_django import types


class Node(object):
    """Base class to define queryset filters for all nodes."""

    # will be set in core.AppConfig.ready hook, see apps.py
    # to avoid recursive import error
    visibility_classes = None

    @classmethod
    def get_queryset(cls, queryset, info):
        if cls.visibility_classes is None:
            raise ImproperlyConfigured(
                "check that app `caluma.core` is part of your `INSTALLED_APPS` "
                "or custom node has `visibility_classes` properly assigned."
            )

        for visibility_class in cls.visibility_classes:
            queryset = visibility_class().filter_queryset(cls, queryset, info)

        return queryset.select_related()


class DjangoObjectType(Node, types.DjangoObjectType):
    """
    Django object type with overwriting get_queryset support.

    Inspired by https://github.com/graphql-python/graphene-django/pull/528/files
    and might be removed once merged.
    """

    @classmethod
    def get_node(cls, info, id):
        queryset = cls.get_queryset(cls._meta.model.objects, info)
        return queryset.filter(pk=id).first()

    class Meta:
        abstract = True


class CountableConnectionBase(graphene.Connection):
    """Connection subclass that supports totalCount."""

    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        if isinstance(self.iterable, QuerySet):
            return self.iterable.count()
        return len(self.iterable)
