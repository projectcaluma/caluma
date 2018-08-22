from collections import OrderedDict

import graphene
from graphene.types import Field, InputField
from graphene.types.objecttype import yank_fields_from_attrs
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework.mutation import (
    SerializerMutation,
    SerializerMutationOptions,
    fields_for_serializer,
)


class NodeSerializerMutationOptions(SerializerMutationOptions):
    return_field_name = None


class NodeSerializerMutation(SerializerMutation):
    """
    Returns a node of given serializer model instead of serializing data directly.

    This is a fix for following issue:
    https://github.com/graphql-python/graphene-django/issues/376

    Once this has been proven to be a good abstraction an upstream PR
    should be provided.
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        lookup_field=None,
        serializer_class=None,
        model_class=None,
        model_operations=["create", "update"],
        return_field_name=None,
        only_fields=(),
        exclude_fields=(),
        **options
    ):

        if not serializer_class:  # pragma: no cover
            raise Exception("serializer_class is required for the SerializerMutation")

        if (
            "update" not in model_operations and "create" not in model_operations
        ):  # pragma: no cover
            raise Exception('model_operations must contain "create" and/or "update"')

        serializer = serializer_class()
        if model_class is None:
            serializer_meta = getattr(serializer_class, "Meta", None)
            if serializer_meta:
                model_class = getattr(serializer_meta, "model", None)

        if lookup_field is None and model_class:
            lookup_field = model_class._meta.pk.name

        input_fields = fields_for_serializer(
            serializer, only_fields, exclude_fields, is_input=True
        )

        if not return_field_name:
            model_name = model_class.__name__
            return_field_name = model_name[:1].lower() + model_name[1:]

        registry = get_global_registry()
        model_type = registry.get_type_for_model(model_class)
        output_fields = OrderedDict()
        output_fields[return_field_name] = graphene.Field(model_type)

        _meta = NodeSerializerMutationOptions(cls)
        _meta.lookup_field = lookup_field
        _meta.model_operations = model_operations
        _meta.serializer_class = serializer_class
        _meta.model_class = model_class
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)
        _meta.return_field_name = return_field_name

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(SerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def perform_mutate(cls, serializer, info):
        obj = serializer.save()
        kwargs = {cls._meta.return_field_name: obj}
        return cls(errors=None, **kwargs)


class UserDefinedPrimaryKeyNodeSerializerMutation(NodeSerializerMutation):
    """
    Allows a primary key to be overwritten by user.

    TODO: verify whether this makes sense to send upstream.
    """

    class Meta:
        abstract = True

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        lookup_field = cls._meta.lookup_field
        model_class = cls._meta.model_class

        # TODO: needs to verify whether 404 needs to be thrown in case
        # lookup_field is an AutoField
        instance = model_class.objects.filter(
            **{lookup_field: input[lookup_field]}
        ).first()

        return {
            "instance": instance,
            "data": input,
            "context": {"request": info.context},
        }
