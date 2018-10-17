from factory import Faker, django


class DjangoModelFactory(django.DjangoModelFactory):
    created_by_user = Faker("uuid4")
    created_by_group = Faker("uuid4")
