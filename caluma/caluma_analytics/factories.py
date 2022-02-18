from factory import Faker, LazyAttribute, Maybe, SubFactory

from ..caluma_core.factories import DjangoModelFactory
from . import models


class AnalyticsTableFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    starting_object = Faker(
        "word",
        ext_word_list=[i for i, _ in models.AnalyticsTable.STARTING_OBJECT_CHOICES],
    )
    table_type = Faker(
        "word",
        ext_word_list=[i for i, _ in models.AnalyticsTable.TABLE_TYPE_CHOICES],
    )
    base_table = None

    meta = {}

    class Meta:
        model = models.AnalyticsTable


class AnalyticsFieldFactory(DjangoModelFactory):
    alias = Faker("slug")
    meta = {}
    data_source = Faker("slug")
    table = SubFactory(AnalyticsTableFactory)

    function = Maybe(
        "is_pivot",
        yes_declaration=Faker(
            "word",
            ext_word_list=[i for i, _ in models.AnalyticsField.FUNCTION_CHOICES],
        ),
        no_declaration=None,
    )

    class Meta:
        model = models.AnalyticsField

    class Params:
        is_pivot = LazyAttribute(
            lambda f: f.table.table_type == models.AnalyticsTable.TYPE_PIVOT
        )
