from factory import Faker, LazyAttribute, django


class DjangoModelFactory(django.DjangoModelFactory):
    # These are still UUID4, but it's tests only, so we don't really
    # care that much
    created_by_user = Faker("uuid4")
    created_by_group = Faker("uuid4")
    modified_by_user = LazyAttribute(lambda inst: inst.created_by_user)
    modified_by_group = LazyAttribute(lambda inst: inst.created_by_group)
