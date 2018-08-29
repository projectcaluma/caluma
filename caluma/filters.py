from django.utils import translation
from django_filters.rest_framework import Filter


class LocalizedFilter(Filter):
    def filter(self, qs, value):
        lang = translation.get_language()
        filter_expr = "{0}__{1}__{2}".format(self.field_name, lang, self.lookup_expr)
        return qs.filter(**{filter_expr: value})
