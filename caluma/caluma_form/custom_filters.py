# This is just an example

from django_filters.rest_framework import CharFilter, FilterSet

from . import models


class CustomQuestionFilterSet(FilterSet):
    foo = CharFilter(method="filter_foo")

    def filter_foo(self, queryset, name, value):
        return queryset.none()

    class Meta:
        model = models.Question
        fields = ("foo",)
