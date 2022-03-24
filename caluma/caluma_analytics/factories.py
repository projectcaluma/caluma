from factory import Faker, SubFactory

from ..caluma_core.factories import DjangoModelFactory
from . import models


class AnalyticsTableFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    starting_object = Faker(
        "word",
        ext_word_list=[i for i, _ in models.AnalyticsTable.STARTING_OBJECT_CHOICES],
    )

    meta = {}

    class Meta:
        model = models.AnalyticsTable


class AnalyticsFieldFactory(DjangoModelFactory):
    alias = Faker("slug")
    meta = {}
    data_source = Faker("slug")
    table = SubFactory(AnalyticsTableFactory)

    function = Faker(
        "word",
        ext_word_list=[i for i, _ in models.AnalyticsField.FUNCTION_CHOICES],
    )

    class Meta:
        model = models.AnalyticsField
