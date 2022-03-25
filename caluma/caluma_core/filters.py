import enum
from functools import reduce, singledispatch

import graphene
from django import forms
from django.conf import settings
from django.contrib.postgres.fields.hstore import KeyTransform
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import OrderBy, RawSQL
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.utils import translation
from django_filters.conf import settings as filters_settings
from django_filters.constants import EMPTY_VALUES
from django_filters.fields import ChoiceField
from django_filters.rest_framework import (
    CharFilter,
    DateTimeFilter,
    Filter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
)
from graphene import Enum, InputObjectType, List
from graphene.types import generic
from graphene.types.utils import get_type
from graphene.utils.str_converters import to_camel_case, to_snake_case
from graphene_django import filter
from graphene_django.converter import convert_choice_name
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from graphene_django.forms.converter import convert_form_field
from graphene_django.registry import get_global_registry
from localized_fields.fields import LocalizedField
from rest_framework.exceptions import ValidationError

from .forms import (
    GlobalIDFormField,
    GlobalIDMultipleChoiceField,
    SlugMultipleChoiceField,
)
from .ordering import CalumaOrdering
from .relay import extract_global_id
from .types import DjangoConnectionField


class CompositeFieldClass(forms.MultiValueField):
    """Mixin to build complex field classes.

    This is just to pretend to Graphene that it's a composite type.
    It's the base of the internal representation that only passes
    values from the request down to the filters (or similar).

    The actual schema type is generated via the `convert_form_field()`
    function from `graphene_django.forms.converter`.
    """

    def __init__(self, label, *, fields=None, **kwargs):
        fields = (forms.CharField(), forms.CharField())
        super().__init__(fields=fields)

    def clean(self, data):
        # override parent clean() which would reject our data structure.
        # We don't validate, as the structure is already enforced by the
        # schema.

        return data


class AscDesc(Enum):
    ASC = "ASC"
    DESC = "DESC"


class FilterCollectionFilter(Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        filter_coll = self.filterset_class()
        for flt in value:
            if not flt:
                continue
            invert = flt.pop("invert", False)
            flt_key = list(flt.keys())[0]
            flt_val = flt[flt_key]
            filter = filter_coll.filters[flt_key]

            new_qs = filter.filter(qs, flt_val)

            if invert:
                qs = qs.exclude(pk__in=new_qs)
            else:
                qs = new_qs

        return qs


class FilterCollectionOrdering(Filter):
    def _order_part(self, qs, ord, filter_coll):
        direction = ord.pop("direction", "ASC")

        assert len(ord) == 1
        filt_name = list(ord.keys())[0]
        filter = filter_coll.filters[filt_name]
        qs, field = filter.get_ordering_value(qs, ord[filt_name])

        # Normally, people use ascending order, and in this context it seems
        # natural to have NULL entries at the end.
        # Making the `nulls_first`/`nulls_last` parameter accessible in the
        # GraphQL interface would be overkill, at least for now.
        return (
            qs,
            OrderBy(
                field,
                descending=(direction == "DESC"),
                nulls_first=(direction == "DESC"),
                nulls_last=(direction == "ASC"),
            ),
        )

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        filter_coll = self.filterset_class()

        order_by = []
        for ord in value:
            qs, order_field = self._order_part(qs, ord, filter_coll)
            order_by.append(order_field)

        if order_by:
            qs = qs.order_by(*order_by)

        return qs


def FilterCollectionFactory(filterset_class, ordering):  # noqa:C901
    """
    Build a single filter from a `FilterSet`.

    This converts an arbitrary `FilterSet` class into a single filter that
    allows chaining of filters as a list. In addition, this introduces
    an optional `invert` parameter, allowing requestors to use
    a filter for either inclusion or exclusion.

    On the schema side, this generates a new type to represent the filter value
    whose name is derived from the given filterset class.

    Usage:
    >>> class MyFilterSet(FilterSet):
    ...     filter = FilterCollectionFactory(FilterSetWithActualFilters, ordering=False)

    """

    field_class_name = f"{filterset_class.__name__}Field"
    field_type_name = f"{filterset_class.__name__}Type"
    collection_name = f"{filterset_class.__name__}Collection"

    # The field class.
    custom_field_class = type(field_class_name, (CompositeFieldClass,), {})

    @convert_form_field.register(custom_field_class)
    def convert_field(field):

        registry = get_global_registry()
        converted = registry.get_converted_field(field)
        if converted:
            return converted

        _filter_coll = filterset_class()

        def _get_or_make_field(name, filt):
            return convert_form_field(filt.field)

        def _should_include_filter(filt):
            # if we're in ordering mode, we want
            # to return True for all CalumaOrdering types,
            # and if it's false, we want the opposite
            return ordering == isinstance(filt, CalumaOrdering)

        filter_fields = {
            name: _get_or_make_field(name, filt)
            for name, filt in _filter_coll.filters.items()
            # exclude orderBy in our fields. We want only new-style order filters
            if _should_include_filter(filt) and name != "orderBy"
        }

        if ordering:
            filter_fields["direction"] = AscDesc(default=AscDesc.ASC, required=False)
        else:
            filter_fields["invert"] = graphene.Boolean(required=False, default=False)

        filter_type = type(field_type_name, (InputObjectType,), filter_fields)

        converted = List(filter_type)
        registry.register_converted_field(field, converted)
        return converted

    filter_impl = FilterCollectionOrdering if ordering else FilterCollectionFilter

    filter_coll = type(
        collection_name,
        (filter_impl,),
        {"field_class": custom_field_class, "filterset_class": filterset_class},
    )
    return filter_coll()


def CollectionFilterSetFactory(filterset_class, orderset_class=None):
    """
    Build single-filter filterset classes.

    Use this in place of a regular filterset_class parametrisation in
    the serializers.
    If you pass the optional `orderset_class` parameter, it is used for
    an `order` filter. The filters defined in the `orderset_class` must
    inherit from `caluma.caluma_core.ordering.CalumaOrdering` and provide a
    `get_ordering_value()` method.

    Example:
    >>> all_documents = DjangoFilterConnectionField(
    ...    Document, filterset_class=CollectionFilterSetFactory(DocumentFilterSet)
    ... )

    """

    suffix = "" if orderset_class else "NoOrdering"
    cache_key = filterset_class.__name__ + suffix

    if cache_key in CollectionFilterSetFactory._cache:
        return CollectionFilterSetFactory._cache[cache_key]

    coll_fields = {"filter": FilterCollectionFactory(filterset_class, ordering=False)}
    if orderset_class:
        coll_fields["order"] = FilterCollectionFactory(orderset_class, ordering=True)

    ret = CollectionFilterSetFactory._cache[cache_key] = type(
        f"{filterset_class.__name__}Collection",
        (filterset_class, FilterSet),
        {
            **coll_fields,
            "Meta": type(
                "Meta",
                (filterset_class.Meta,),
                {
                    "model": filterset_class.Meta.model,
                    "fields": filterset_class.Meta.fields + tuple(coll_fields.keys()),
                },
            ),
        },
    )

    return ret


CollectionFilterSetFactory._cache = {}


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


class SlugMultipleChoiceFilter(MultipleChoiceFilter):
    field_class = SlugMultipleChoiceField

    def filter(self, qs, value):
        return super().filter(qs, value)


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
        elif isinstance(model_field, models.JSONField):
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

    This filter additionally allows sorting by meta field values.
    """

    base_field_class = ListField
    field_class = OrderingField

    def __init__(self, label, *args, fields=tuple(), **kwargs):
        fields = tuple(fields) + (
            "created_at",
            "modified_at",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
            *[f"meta_{f}" for f in settings.META_FIELDS],
        )

        super().__init__(
            *args,
            fields=fields,
            label=label,
            empty_label=None,
            null_label=None,
            **kwargs,
        )

    def get_ordering_value(self, param):
        if not any(param.startswith(prefix) for prefix in ("meta_", "-meta_")):
            return super().get_ordering_value(param)

        descending = False
        if param.startswith("-"):
            descending = True
            param = param[1:]

        meta_field_key = param[5:]

        # order_by works on json field keys only without dashes
        # but we want to support dasherized keys as well as this is
        # valid json, hence need to use raw sql
        return OrderBy(
            RawSQL(f'"{self.model._meta.db_table}"."meta"->%s', (meta_field_key,)),
            descending=descending,
        )


class IntegerFilter(Filter):
    field_class = forms.IntegerField


class FilterSet(GrapheneFilterSetMixin, FilterSet):
    created_by_user = CharFilter()
    created_by_group = CharFilter()
    modified_by_user = CharFilter()
    modified_by_group = CharFilter()

    created_before = DateTimeFilter(
        field_name="created_at",
        lookup_expr="lt",
        label="Only return entries created after the given DateTime (Exclusive)",
    )
    created_after = DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
        label="Only return entries created at or before the given DateTime (Inclusive)",
    )


class JSONLookupMode(Enum):
    EXACT = "exact"
    STARTSWITH = "startswith"
    CONTAINS = "contains"
    ICONTAINS = "icontains"
    IN = "in"
    GTE = "gte"
    GT = "gt"
    LTE = "lte"
    LT = "lt"


class JSONValueFilterType(InputObjectType):
    key = graphene.String(required=True)
    value = generic.GenericScalar(required=True)
    lookup = JSONLookupMode()


class JSONValueFilterField(CompositeFieldClass):
    pass


class JSONValueFilter(Filter):
    field_class = JSONValueFilterField

    def __init__(self, *args, lookup_expr=None, **kwargs):
        if lookup_expr is None:
            lookup_expr = JSONLookupMode.get(filters_settings.DEFAULT_LOOKUP_EXPR)
        super().__init__(*args, lookup_expr=lookup_expr, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        for expr in value:
            if expr in EMPTY_VALUES:  # pragma: no cover
                continue

            lookup = expr.get("lookup") or self.lookup_expr
            lookup_expr = (hasattr(lookup, "value") and lookup.value) or lookup

            # "contains" behaves differently on JSONFields as it does on TextFields.
            # That's why we annotate the queryset with the value.
            # Some discussion about it can be found here:
            # https://code.djangoproject.com/ticket/26511
            if isinstance(expr["value"], str):
                qs = qs.annotate(
                    field_val=Cast(
                        KeyTextTransform(expr["key"], self.field_name),
                        models.CharField(),
                    ),
                )
                lookup = {f"field_val__{lookup_expr}": expr["value"]}
            else:
                lookup = {
                    f"{self.field_name}__{expr['key']}__{lookup_expr}": expr["value"]
                }
            qs = qs.filter(**lookup)
        return qs

    @staticmethod
    @convert_form_field.register(JSONValueFilterField)
    def convert_meta_value_field(field):
        registry = get_global_registry()
        converted = registry.get_converted_field(field)
        if converted:
            return converted

        converted = List(JSONValueFilterType)
        registry.register_converted_field(field, converted)
        return converted


class MetaFilterSet(FilterSet):
    meta_has_key = CharFilter(lookup_expr="has_key", field_name="meta")
    meta_value = JSONValueFilter(field_name="meta")


class DjangoFilterConnectionField(
    filter.DjangoFilterConnectionField, DjangoConnectionField
):
    @property
    def filterset_class(self):
        return self._provided_filterset_class

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        max_limit,
        enforce_first_or_last,
        root,
        info,
        **args,
    ):
        return super().connection_resolver(
            resolver=resolver,
            connection=connection,
            default_manager=default_manager,
            queryset_resolver=queryset_resolver,
            max_limit=max_limit,
            enforce_first_or_last=enforce_first_or_last,
            root=root,
            info=info,
            **cls._clean_args_for_queryset_resolver(args),
        )

    @classmethod
    def _clean_args_for_queryset_resolver(cls, args):
        # Graphene parses incoming data into Enums too early, thus our filters
        # will receive enum objects that cannot be parsed
        #
        # TODO: check if this is still required after the below
        # resolve_queryset() is completely implemented (we assumed it's
        # the Enums, but it was actually the list in order_by. We'll keep
        # it here until we KNOW we can remove it again..)
        @singledispatch
        def clean(data):
            return data

        @clean.register(enum.Enum)
        def _(data):
            return data.value

        @clean.register(list)
        def _(data):
            return [clean(e) for e in data]

        @clean.register(dict)
        def _(data):
            return {k: clean(v) for k, v in data.items()}

        return clean(args)

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        # Overload the parent class' resolve_queryset() because (for now)
        # it is unable to deal with multiple order_by values. It's more or less
        # a literal copy of DjangoFilterConnectionField.resolve_queryset() except
        # for a "better" filter_kwargs() that doesn't fail on lists in the order_by
        # parameter.
        def filter_kwargs():
            kwargs = {}
            for k, v in args.items():
                if k in filtering_args:
                    if k == "order_by" and v is not None:
                        # in Caluma, order_by is always a list
                        assert isinstance(v, list)
                        v = [to_snake_case(e) for e in v]
                    kwargs[k] = v
            return kwargs

        qs = connection._meta.node.get_queryset(iterable, info)

        filterset = filterset_class(
            data=filter_kwargs(), queryset=qs, request=info.context
        )
        if filterset.form.is_valid():
            return filterset.qs
        raise ValidationError(filterset.form.errors.as_json())  # pragma: no cover


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

    if field.label in convert_ordering_field_to_enum._cache:
        return convert_ordering_field_to_enum._cache[field.label]

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
    convert_ordering_field_to_enum._cache[field.label] = converted
    return converted


convert_ordering_field_to_enum._cache = {}


@convert_form_field.register(forms.ChoiceField)
@convert_form_field.register(ChoiceField)
def convert_choice_field_to_enum(field):
    """
    Add support to convert ordering choices to Graphql enum.

    Label is used as enum name.
    """

    registry = get_global_registry()

    # field label of enum needs to be unique so stored it likewise
    converted = registry.get_converted_field(field.label)
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

    registry.register_converted_field(field.label, converted)
    return converted


class _ExtractNestedListFilterMixin:
    def filter(self, qs, value):
        if isinstance(value, list) and len(value) and isinstance(value[0], list):
            # TODO: this seems to be a workaround - we shouldn't
            # get a double-nested list here. However the schema
            # seems to show it as such...
            value = [val for sublist in value for val in sublist]
        return super().filter(qs, value)


def generate_list_filter_class(inner_type):
    """
    Return a Filter class that will resolve into a List(`inner_type`) graphene type.

    This allows us to do things like use `__in` and `__overlap` filters that accept
    graphene lists instead of a comma delimited value string that's interpolated into
    a list by django_filters.BaseCSVFilter (which is used to define
    django_filters.BaseInFilter)
    """

    form_field = type(f"List{inner_type.__name__}FormField", (forms.Field,), {})
    filter_class = type(
        f"{inner_type.__name__}ListFilter",
        (
            _ExtractNestedListFilterMixin,
            Filter,
        ),
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

    def do_convert_type(x):
        return graphene.List(inner_type, required=x.required)

    convert_form_field.register(form_field)(do_convert_type)

    return filter_class


StringListFilter = generate_list_filter_class(graphene.String)
