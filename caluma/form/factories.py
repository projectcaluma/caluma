from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models


class FormSpecificationFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False

    class Meta:
        model = models.FormSpecification


class QuestionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.Question.TYPE_CHOICES)
    is_required = "true"
    is_hidden = "false"
    configuration = {}
    meta = {}
    is_archived = False

    class Meta:
        model = models.Question


class OptionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    meta = {}

    class Meta:
        model = models.Option


class QuestionOptionFactory(DjangoModelFactory):
    option = SubFactory(OptionFactory)
    question = SubFactory(QuestionFactory)
    sort = 0

    class Meta:
        model = models.QuestionOption


class FormSpecificationQuestionFactory(DjangoModelFactory):
    form_specification = SubFactory(FormSpecificationFactory)
    question = SubFactory(QuestionFactory)
    sort = 0

    class Meta:
        model = models.FormSpecificationQuestion
