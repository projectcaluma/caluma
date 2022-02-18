from django_filters.rest_framework import FilterSet

from ..caluma_core.filters import MetaFilterSet, SearchFilter, SlugMultipleChoiceFilter
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from . import models


class AnalyticsTableFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name"))
    slugs = SlugMultipleChoiceFilter(field_name="slug")

    class Meta:
        model = models.AnalyticsTable
        fields = (
            "slug",
            "name",
        )


class AnalyticsFieldFilterSet(MetaFilterSet):
    search = SearchFilter(
        fields=(
            "alias",
            "data_source",
            "function",
            "table__name",
            "source_field__alias",
        )
    )
    slugs = SlugMultipleChoiceFilter(field_name="slug")

    class Meta:
        model = models.AnalyticsField
        fields = (
            "alias",
            "table",
        )


class AnalyticsTableOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.AnalyticsTable,
        fields=[
            "created_at",
            "modified_at",
            "created_by_user",
            "created_by_group",
            "modified_by_user",
            "modified_by_group",
            "slug",
            "name",
        ],
    )

    class Meta:
        model = models.AnalyticsTable
        fields = ("meta", "attribute")
