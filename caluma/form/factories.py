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


class QuestionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("name")
    type = Faker("word", ext_word_list=models.Question.TYPE_CHOICES)
    is_required = "true"
    is_hidden = "false"
    configuration = {}
    meta = {}

    class Meta:
        model = models.Question
