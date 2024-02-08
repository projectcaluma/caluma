from django_filters.rest_framework import FilterSet, MultipleChoiceFilter

from ..caluma_core.filters import MetaFilterSet, SearchFilter
from ..caluma_core.ordering import AttributeOrderingFactory, MetaFieldOrdering
from . import models


class AnalyticsTableFilterSet(MetaFilterSet):
    search = SearchFilter(fields=("slug", "name", "description"))
    slugs = MultipleChoiceFilter(field_name="slug")

    class Meta:
        model = models.AnalyticsTable
        fields = ("slug", "name", "description")


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
    slugs = MultipleChoiceFilter(field_name="slug")

    class Meta:
        model = models.AnalyticsField
        fields = (
            "alias",
            "table",
        )


class AnalyticsFieldOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.AnalyticsField,
        fields=["created_at", "modified_at", "alias"],
    )

    class Meta:
        model = models.AnalyticsField
        fields = ("meta", "attribute")


class AnalyticsTableOrderSet(FilterSet):
    meta = MetaFieldOrdering()
    attribute = AttributeOrderingFactory(
        models.AnalyticsTable,
        fields=["created_at", "modified_at", "slug", "name", "description"],
    )

    class Meta:
        model = models.AnalyticsTable
        fields = ("meta", "attribute")
