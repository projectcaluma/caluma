from collections import OrderedDict
from functools import singledispatch

import graphene
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from graphene.relay.mutation import ClientIDMutation
from graphene.types import Field, InputField
from graphene.types.mutation import MutationOptions
from graphene.types.objecttype import yank_fields_from_attrs
from graphene_django.converter import convert_django_field, convert_field_to_string
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework.mutation import fields_for_serializer
from graphql.language import ast
from localized_fields.fields import LocalizedField
from rest_framework import exceptions

from .relay import extract_global_id


class ASTAnalyzer:
    @staticmethod
    def get_mutation_params(info):
        @singledispatch
        def _parse_ast_value(arg, info):  # pragma: no cover
            raise RuntimeError(f"Unknown arg {arg}")

        @_parse_ast_value.register(ast.ObjectValue)
        def _(arg, info):
            return {
                field.name.value: _parse_ast_value(field.value, info)
                for field in arg.fields
            }

        @_parse_ast_value.register(ast.ListValue)
        def _(arg, info):
            return [_parse_ast_value(val, info) for val in arg.values]

        @_parse_ast_value.register(ast.StringValue)
        def _(arg, info):
            return arg.value

        @_parse_ast_value.register(ast.Variable)
        def _(arg, info):
            return info.variable_values[arg.name.value]

        # No need to keep the registered singledispatch implementation
        # in the namespace
        del _

        current_sel = [
            sel
            for sel in info.operation.selection_set.selections
            if sel.name.value == info.field_name
            # if aliases are used, we need to compare them as well
            and (sel.alias is None or sel.alias.value == info.path[0])
        ][0]

        return {
            arg.name.value: _parse_ast_value(arg.value, info)
            for arg in current_sel.arguments
        }


convert_django_field.register(LocalizedField, convert_field_to_string)


class MutationOptions(MutationOptions):
    lookup_field = None
    lookup_input_kwarg = None
    model_class = None
    model_operations = ["create", "update"]
    serializer_class = None
    return_field_name = None
    return_field_type = None


class Mutation(ClientIDMutation):
    """
    Caluma specific Mutation solving following upstream issues.

    1. Expose node instead of attributes directly.

    Dependend issues:
    https://github.com/graphql-python/graphene-django/issues/376
    https://github.com/graphql-python/graphene-django/issues/386
    https://github.com/graphql-python/graphene-django/issues/462

    2. Validation should be GraphQL errors

    https://github.com/graphql-python/graphene-django/issues/380

    Goal would be to get rid of this custom class when referenced issues
    have been resolved successfully.


    The following `Meta` attributes control the basic behavior:
    * `lookup_field`: The model field that should be used to for performing object lookup of
      individual model instances. Defaults to 'pk'.
    * `lookup_input_kwarg`: Input argument that should be used for object lookup.
      Defaults to 'lookup_field'
    * `serializer_class`: The serializer class that should be used for validating, deserializing input
      and performing side effect.
    * `model_class`: The model class to lookup instance of. Defaults to model of serializer.
    * `model_operations`: Define which operations are allowed. Defaults to `['create', 'update'].
    * `fields`: Restrict input fields. Defaults to serializer fields.
    * `exclude`: Exclude input fields. Defaults to serializer fields.
    * `return_field_name`: Name of return graph. Defaults to camel cased model class name.
                           Maybe set to False to not return a field at all.
    * `return_field_type`: Type of return graph. Defaults to object type of given model_class.
    """

    class Meta:
        abstract = True

    # will be set in caluma_core.AppConfig.ready hook, see apps.py
    # to avoid recursive import error
    permission_classes = None

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        lookup_field=None,
        lookup_input_kwarg=None,
        serializer_class=None,
        model_class=None,
        model_operations=None,
        fields=(),
        exclude=(),
        return_field_name=None,
        return_field_type=None,
        **options,
    ):
        model_operations = (
            model_operations if model_operations else ["create", "update"]
        )
        if not serializer_class:
            raise Exception("serializer_class is required for the Mutation")

        if "update" not in model_operations and "create" not in model_operations:
            raise Exception('model_operations must contain "create" and/or "update"')

        serializer = serializer_class()
        if model_class is None:
            serializer_meta = getattr(serializer_class, "Meta", None)
            if serializer_meta:
                model_class = getattr(serializer_meta, "model", None)

        if lookup_field is None and model_class:
            lookup_field = model_class._meta.pk.name
        if lookup_input_kwarg is None:
            lookup_input_kwarg = lookup_field

        input_fields = fields_for_serializer(serializer, fields, exclude, is_input=True)

        if return_field_name is None:
            model_name = model_class.__name__
            return_field_name = model_name[:1].lower() + model_name[1:]

        if not return_field_type:
            registry = get_global_registry()
            return_field_type = registry.get_type_for_model(model_class)

        output_fields = OrderedDict()
        if return_field_name:
            output_fields[return_field_name] = graphene.Field(return_field_type)

        _meta = MutationOptions(cls)
        _meta.lookup_field = lookup_field
        _meta.lookup_input_kwarg = lookup_input_kwarg
        _meta.model_operations = model_operations
        _meta.serializer_class = serializer_class
        _meta.model_class = model_class
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)
        _meta.return_field_name = return_field_name
        _meta.return_field_type = return_field_type

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super().__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        model_class = cls._meta.model_class
        return_field_type = cls._meta.return_field_type

        if model_class:
            instance = cls.get_object(
                root,
                info,
                return_field_type.get_queryset(
                    model_class.objects.select_related(), info
                ),
                **input,
            )
            return {
                "instance": instance,
                "data": input,
                "context": {"request": info.context, "info": info, "mutation": cls},
            }

        return {"data": input, "context": {"request": info.context, "info": info}}

    @classmethod
    def get_object(cls, root, info, queryset, **input):
        lookup_field = cls._meta.lookup_field
        lookup_input_kwarg = cls._meta.lookup_input_kwarg

        if "update" in cls._meta.model_operations and lookup_input_kwarg in input:
            instance = get_object_or_404(
                queryset, **{lookup_field: extract_global_id(input[lookup_input_kwarg])}
            )
        elif "create" in cls._meta.model_operations:
            instance = None
        else:
            raise Exception(
                'Invalid update operation. Input parameter "{0}" required.'.format(
                    lookup_field
                )
            )

        return instance

    @classmethod
    def check_permissions(cls, root, info):
        if cls.permission_classes is None:
            raise ImproperlyConfigured(
                "check that app `caluma.caluma_core` is part of your `INSTALLED_APPS` "
                "or custom mutation has `permission_classes` properly assigned."
            )

        for permission_class in cls.permission_classes:
            if not permission_class().has_permission(cls, info):
                raise exceptions.PermissionDenied()

    @classmethod
    def check_object_permissions(cls, root, info, instance):
        for permission_class in cls.permission_classes:
            if not permission_class().has_object_permission(cls, info, instance):
                raise exceptions.PermissionDenied()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        cls.check_permissions(root, info)
        kwargs = cls.get_serializer_kwargs(root, info, **input)
        instance = kwargs.get("instance")
        if instance is not None:
            cls.check_object_permissions(root, info, kwargs.get("instance"))

        serializer = cls._meta.serializer_class(**kwargs)

        # TODO: use extensions of error to define what went wrong in validation
        # also see https://github.com/graphql-python/graphql-core/pull/204
        # potentially split each validation error into on GraphQL error
        serializer.is_valid(raise_exception=True)
        return cls.perform_mutate(serializer, info)

    @classmethod
    def perform_mutate(cls, serializer, info):

        obj = serializer.save()
        kwargs = {}
        if cls._meta.return_field_name:
            kwargs[cls._meta.return_field_name] = obj
        return cls(**kwargs)

    @classmethod
    def get_params(cls, info):
        return ASTAnalyzer.get_mutation_params(info)


class UserDefinedPrimaryKeyMixin(object):
    """
    Allows a primary key to be overwritten by user.

    TODO: verify whether this makes sense to send upstream.
    """

    class Meta:
        abstract = True

    @classmethod
    def get_object(cls, root, info, queryset, **input):
        lookup_field = cls._meta.lookup_field
        lookup_input_kwarg = cls._meta.lookup_input_kwarg
        model_class = cls._meta.model_class

        filter_kwargs = {lookup_field: input[lookup_input_kwarg]}
        instance = queryset.filter(**filter_kwargs).first()

        if instance is None and model_class.objects.filter(**filter_kwargs).exists():
            # disallow editing of instances which are not visible by current user
            raise Http404(
                "No %s matches the given query." % queryset.model._meta.object_name
            )

        if instance is None and "create" not in cls._meta.model_operations:
            raise exceptions.ValidationError("Create model operation not allowed.")

        if instance is not None and "update" not in cls._meta.model_operations:
            raise exceptions.ValidationError("Update model operation not allowed.")

        return instance
