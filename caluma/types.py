from django.conf import settings
from django.utils.module_loading import import_string
from graphene_django import types


class Node(object):
    """Base class to define queryset filters for all nodes."""

    visibility_classes = [import_string(cls) for cls in settings.VISIBILITY_CLASSES]

    @classmethod
    def get_queryset(cls, queryset, info):
        for visibility_class in cls.visibility_classes:
            queryset = visibility_class().get_queryset(cls, queryset, info)

        return queryset


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
