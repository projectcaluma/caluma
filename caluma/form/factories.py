from factory import Faker
from factory.django import DjangoModelFactory

from . import models


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    username = Faker("uuid")
    email = Faker("safe_email")

    class Meta:
        model = models.User
