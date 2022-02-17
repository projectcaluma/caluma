from typing import Any, Tuple, Union

from django import forms
from django.db.models.expressions import CombinedExpression, F, Value
from django.db.models.query import QuerySet
from django_filters.fields import ChoiceField
from django_filters.rest_framework import Filter
from graphene import Enum
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry
from rest_framework import exceptions

OrderingFieldType = Union[F, str]


class CalumaOrdering(Filter):
    """Base class for new-style ordering filters.

    This is not really a filter in the rest framework sense,
    but we use it's infrastructure to get conversion to GraphQL
    types.

    This is an abstract base class. To use it, you need to
    implement the `get_ordering_value()` method to return a tuple
    of `(queryset, ordering_field)`. The queryset may be modified,
    for example if you need to annotate it to get to the desired
    ordering field.
    """

    def get_ordering_value(
        self, qs: QuerySet, value: Any
    ) -> Tuple[QuerySet, OrderingFieldType]:  # pragma: no cover
        raise NotImplementedError("get_ordering_value() needs to be implemented")


class MetaFieldOrdering(CalumaOrdering):
    """Ordering filter for ordering by `meta` values."""

    def __init__(self, field_name="meta"):
        super().__init__()
        self.field_name = field_name

    field_class = forms.CharField

    def get_ordering_value(
        self, qs: QuerySet, value: Any
    ) -> Tuple[QuerySet, OrderingFieldType]:
        value = (hasattr(value, "value") and value.value) or value  # noqa: B009

        return qs, CombinedExpression(F(self.field_name), "->", Value(value))


class AttributeOrderingMixin(CalumaOrdering):
    def get_ordering_value(self, qs, value):
        value = (hasattr(value, "value") and value.value) or value  # noqa: B009
        if value not in self._fields:  # pragma: no cover
            # this is normally covered by graphene enforcing its schema,
            # but we still need to handle it
            raise exceptions.ValidationError(
                f"Field '{value}' not available for sorting on {qs.model.__name}"
            )
        return qs, F(value)


def AttributeOrderingFactory(model, fields=None, exclude_fields=None):
    """Build ordering field for a given model.

    Used to define an ordering field that is presented as an enum
    """
    if not exclude_fields:
        exclude_fields = []

    if not fields:
        fields = [f.name for f in model._meta.fields if f.name not in exclude_fields]

    field_enum = type(
        f"Sortable{model.__name__}Attributes",
        (Enum,),
        {field.upper(): field for field in fields},
    )

    field_class = type(f"{model.__name__}AttributeField", (ChoiceField,), {})

    ordering_class = type(
        f"{model.__name__}AttributeOrdering",
        (AttributeOrderingMixin, CalumaOrdering),
        {"field_class": field_class, "_fields": fields},
    )

    @convert_form_field.register(field_class)
    def to_enum(field):
        registry = get_global_registry()
        converted = registry.get_converted_field(field)

        if converted:  # pragma: no cover
            return converted

        converted = field_enum()

        registry.register_converted_field(field, converted)
        return converted

    return ordering_class()
