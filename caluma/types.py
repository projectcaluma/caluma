from django.conf import settings
from graphene_django import types


class QuerysetMixin(object):
    """Filter queryset by configured visibility classes."""

    @classmethod
    def get_queryset(cls, queryset, info):
        for visibility_class in settings.VISIBILITY_CLASSES:
            queryset = visibility_class().get_queryset(cls, queryset, info)

        return queryset


class DjangoObjectType(QuerysetMixin, types.DjangoObjectType):
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
