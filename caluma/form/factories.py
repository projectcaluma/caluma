from factory import Faker
from factory.django import DjangoModelFactory

from . import models


class FormFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("name")
    description = Faker("text")
    meta = {}
    is_published = False
    is_archived = False

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
    is_archived = False

    class Meta:
        model = models.Question
