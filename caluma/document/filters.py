from . import models
from ..filters import FilterSet, SearchFilter


class DocumentFilterSet(FilterSet):
    search = SearchFilter(fields=("answers__value",))

    class Meta:
        model = models.Document
        fields = ("form_specification", "search")
