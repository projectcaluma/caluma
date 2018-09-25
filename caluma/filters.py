from functools import reduce

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.hstore import KeyTransform
from django.contrib.postgres.search import SearchVector
from django.db.models import TextField
from django.db.models.constants import LOOKUP_SEP
from django.db.models.functions import Cast
from django.utils import translation
from django_filters import Filter, FilterSet
from django_filters.constants import EMPTY_VALUES
from graphene.types.utils import get_type
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from localized_fields.fields import LocalizedField


class LocalizedFilter(Filter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        lang = translation.get_language()
        filter_expr = "{0}__{1}__{2}".format(self.field_name, lang, self.lookup_expr)
        return qs.filter(**{filter_expr: value})


GrapheneFilterSetMixin.FILTER_DEFAULTS.update(
    {LocalizedField: {"filter_class": LocalizedFilter}}
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
            return Cast(field_lookup, TextField())

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


class FilterSet(GrapheneFilterSetMixin, FilterSet):
    pass


class DjangoFilterSetConnectionField(DjangoFilterConnectionField):
    @property
    def filterset_class(self):
        return self._provided_filterset_class

    @property
    def model(self):
        return self.filterset_class._meta.model

    @property
    def type(self):
        return get_type(self._type)
