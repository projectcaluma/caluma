from functools import reduce

import django.forms
import graphene
from django import forms
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.hstore import KeyTransform
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.functions import Cast
from django.utils import translation
from django_filters.constants import EMPTY_VALUES
from django_filters.fields import ChoiceField
from django_filters.rest_framework import (
    CharFilter,
    ChoiceFilter,
    Filter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
)
from graphene import Enum, InputObjectType, List
from graphene.types.utils import get_type
from graphene.types import generic
from graphene.utils.str_converters import to_camel_case
from graphene_django import filter
from graphene_django.converter import convert_choice_name
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry
from localized_fields.fields import LocalizedField

from .forms import GlobalIDFormField, GlobalIDMultipleChoiceField
from .relay import extract_global_id


class GlobalIDFilter(Filter):
    field_class = GlobalIDFormField

    def filter(self, qs, value):
        _id = None
        if value is not None:
            _id = extract_global_id(value)
        return super(GlobalIDFilter, self).filter(qs, _id)


class GlobalIDMultipleChoiceFilter(MultipleChoiceFilter):
    field_class = GlobalIDMultipleChoiceField

    def filter(self, qs, value):
        gids = [extract_global_id(v) for v in value]
        return super(GlobalIDMultipleChoiceFilter, self).filter(qs, gids)


class LocalizedFilter(Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        lang = translation.get_language()
        filter_expr = "{0}__{1}__{2}".format(self.field_name, lang, self.lookup_expr)
        return qs.filter(**{filter_expr: value})


GrapheneFilterSetMixin.FILTER_DEFAULTS.update(
    {
        LocalizedField: {"filter_class": LocalizedFilter},
        models.AutoField: {"filter_class": GlobalIDFilter},
        models.OneToOneField: {"filter_class": GlobalIDFilter},
        models.ForeignKey: {"filter_class": GlobalIDFilter},
        models.ManyToManyField: {"filter_class": GlobalIDMultipleChoiceFilter},
        models.ManyToOneRel: {"filter_class": GlobalIDMultipleChoiceFilter},
        models.ManyToManyRel: {"filter_class": GlobalIDMultipleChoiceFilter},
    }
)


class SearchFilter(Filter):
    """
    Enable fulltext search on queryset.

    Define fields which need to be searched in.
    """

    def __init__(self, *args, fields, **kwargs):
        self.fields = fields
        super().__init__(*args, **kwargs)

    def _get_model_field(self, model, field):
        model_field = model._meta.get_field(field)
        return model_field, getattr(model_field, "related_model", None)

    def _build_search_expression(self, field_lookup):
        # TODO: is there no Django API which allows conversion of lookup to django field?
        model_field, _ = reduce(
            lambda model_tuple, field: self._get_model_field(model_tuple[1], field),
            field_lookup.split(LOOKUP_SEP),
            (None, self.model),
        )

        if isinstance(model_field, LocalizedField):
            lang = translation.get_language()
            return KeyTransform(lang, field_lookup)
        elif isinstance(model_field, JSONField):
            return Cast(field_lookup, models.TextField())

        return field_lookup

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        qs = qs.annotate(
            search=SearchVector(
                *[self._build_search_expression(field) for field in self.fields]
            )
        )

        return qs.filter(search=value)


class OrderingField(ChoiceField):
    """
    Specific ordering field used as marker to convert to graphql type.

    See `convert_ordering_field_to_enum`
    """

    def validate(self, value):
        invalid = set(value or []) - {choice[0] for choice in self.choices}
        return not bool(invalid)

    def to_python(self, value):
        return value


class ListField(forms.Field):
    """List field as to allow actual lists in ordering vs csv string."""

    pass


class OrderingFilter(OrderingFilter):
    """Ordering filter adding default fields from models.BaseModel.

    Label is required and is used for enum naming in GraphQL schema.
    """

    base_field_class = ListField
    field_class = OrderingField

    def __init__(self, label, *args, fields=tuple(), **kwargs):
        fields = tuple(fields) + (
            "created_at",
            "modified_at",
            "created_by_user",
            "created_by_group",
        )

        super().__init__(
            *args,
            fields=fields,
            label=label,
            empty_label=None,
            null_label=None,
            **kwargs,
        )


class FilterSet(GrapheneFilterSetMixin, FilterSet):
    created_by_user = CharFilter()
    created_by_group = CharFilter()

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        filter_class, params = super().filter_for_lookup(field, lookup_type)
        if issubclass(filter_class, ChoiceFilter):
            meta = field.model._meta
            # Postfixing newly created filter with Argument to avoid conflicts
            # with query nodes
            name = to_camel_case(f"{meta.object_name}_{field.name}_argument")
            params["label"] = name
        return filter_class, params


class MetaLookupMode(Enum):
    EXACT = "exact"
    STARTSWITH = "startswith"
    CONTAINS = "icontains"


class MetaValueFilterType(InputObjectType):
    key = graphene.String(required=True)
    value = generic.GenericScalar(required=True)
    lookup = MetaLookupMode()


class MetaValueFilterField(forms.MultiValueField):
    def __init__(self, label, **kwargs):
        super().__init__(fields=(forms.CharField(), forms.CharField()))

    def clean(self, data):
        # override parent clean() which would reject our data structure.
        # We don't validate, as the structure is already enforced by the
        # schema.
        return data


class MetaValueFilter(Filter):
    field_class = MetaValueFilterField

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        meta_key = value["key"]
        meta_value = value["value"]
        lookup = value.get("lookup", self.lookup_expr)
        return qs.filter(**{f"{self.field_name}__{meta_key}__{lookup}": meta_value})


@convert_form_field.register(MetaValueFilterField)
def convert_meta_value_field(field):
    registry = get_global_registry()
    converted = registry.get_converted_field(field)
    if converted:
        return converted

    converted = MetaValueFilterType()
    registry.register_converted_field(field, converted)
    return converted


class MetaFilterSet(FilterSet):
    meta_has_key = CharFilter(lookup_expr="has_key", field_name="meta")
    meta_value = MetaValueFilter(field_name="meta")


class DjangoFilterConnectionField(filter.DjangoFilterConnectionField):
    """
    Django connection filter field with object type get_queryset support.

    Inspired by https://github.com/graphql-python/graphene-django/pull/528/files
    and might be removed once merged.
    """

    @property
    def filterset_class(self):
        return self._provided_filterset_class

    @classmethod
    def resolve_queryset(cls, connection, queryset, info, **args):
        return connection._meta.node.get_queryset(queryset, info)

    @classmethod
    def merge_querysets(cls, default_queryset, queryset):
        queryset = super().merge_querysets(default_queryset, queryset)
        # avoid query explosion of single relationships
        # may be removed once following issue is fixed:
        # https://github.com/graphql-python/graphene-django/issues/57
        return queryset.select_related()

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        max_limit,
        enforce_first_or_last,
        filterset_class,
        filtering_args,
        root,
        info,
        **args,
    ):
        class QuerysetManager(object):
            def get_queryset(self):
                return cls.resolve_queryset(
                    connection, default_manager.get_queryset(), info, **args
                )

        return super().connection_resolver(
            resolver,
            connection,
            QuerysetManager(),
            max_limit,
            enforce_first_or_last,
            filterset_class,
            filtering_args,
            root,
            info,
            **args,
        )


class DjangoFilterSetConnectionField(DjangoFilterConnectionField):
    @property
    def model(self):
        return self.filterset_class._meta.model

    @property
    def type(self):
        return get_type(self._type)


@convert_form_field.register(OrderingField)
def convert_ordering_field_to_enum(field):
    """
    Add support to convert ordering choices to Graphql enum.

    Label is used as enum name.
    """
    registry = get_global_registry()
    converted = registry.get_converted_field(field)
    if converted:
        return converted

    def get_choices(choices):
        for value, help_text in choices:
            if value[0] != "-":
                name = convert_choice_name(value) + "_ASC"
            else:
                name = convert_choice_name(value[1:]) + "_DESC"
            description = help_text
            yield name, value, description

    name = to_camel_case(field.label)
    choices = list(get_choices(field.choices))
    named_choices = [(c[0], c[1]) for c in choices]
    named_choices_descriptions = {c[0]: c[2] for c in choices}

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return named_choices_descriptions[self.name]

    enum = Enum(name, list(named_choices), type=EnumWithDescriptionsType)
    converted = List(enum, description=field.help_text, required=field.required)

    registry.register_converted_field(field, converted)
    return converted


@convert_form_field.register(ChoiceField)
def convert_choice_field_to_enum(field):
    """
    Add support to convert ordering choices to Graphql enum.

    Label is used as enum name.
    """

    registry = get_global_registry()
    converted = registry.get_converted_field(field)
    if converted:
        return converted

    def get_choices(choices):
        for value, help_text in choices:
            if value:
                name = convert_choice_name(value)
                description = help_text
                yield name, value, description

    name = to_camel_case(field.label)
    choices = list(get_choices(field.choices))
    named_choices = [(c[0], c[1]) for c in choices]
    named_choices_descriptions = {c[0]: c[2] for c in choices}

    class EnumWithDescriptionsType(object):
        @property
        def description(self):
            return named_choices_descriptions[self.name]

    enum = Enum(name, list(named_choices), type=EnumWithDescriptionsType)
    converted = enum(description=field.help_text, required=field.required)

    registry.register_converted_field(field, converted)
    return converted


def _generate_list_filter_class(inner_type):
    """
    Return a Filter class that will resolve into a List(`inner_type`) graphene type.

    This allows us to do things like use `__in` and `__overlap` filters that accept
    graphene lists instead of a comma delimited value string that's interpolated into
    a list by django_filters.BaseCSVFilter (which is used to define
    django_filters.BaseInFilter)
    """

    form_field = type(f"List{inner_type.__name__}FormField", (django.forms.Field,), {})
    filter_class = type(
        f"{inner_type.__name__}ListFilter",
        (Filter,),
        {
            "field_class": form_field,
            "__doc__": (
                f"{inner_type.__name__}ListFilter is a small extension of a raw "
                f"django_filters.Filter that allows us to express graphql "
                f"List({inner_type.__name__}) arguments using FilterSets. "
                f"Note that the given values are passed directly into queryset filters."
            ),
        },
    )
    convert_form_field.register(form_field)(
        lambda x: graphene.List(inner_type, required=x.required)
    )

    return filter_class


StringListFilter = _generate_list_filter_class(graphene.String)
