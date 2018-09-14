from . import models
from ..filters import FilterSet, SearchFilter


class DocumentFilterSet(FilterSet):
    search = SearchFilter(
        fields=("form__slug", "form__name", "form__description", "answers__value")
    )

    class Meta:
        model = models.Document
        fields = ("form", "search")
