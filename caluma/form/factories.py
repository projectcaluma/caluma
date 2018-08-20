from factory import Faker
from factory.django import DjangoModelFactory

from . import models


class FormFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("name")
    description = Faker("text")
    meta = {}

    class Meta:
        model = models.Form
