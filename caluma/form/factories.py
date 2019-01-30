from factory import Faker, SubFactory

from . import models
from ..core.factories import DjangoModelFactory


class FormFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False

    class Meta:
        model = models.Form


class QuestionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.Question.TYPE_CHOICES)
    is_required = "true"
    is_hidden = "false"
    configuration = {}
    meta = {}
    is_archived = False
    row_form = SubFactory(FormFactory)

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


class FormQuestionFactory(DjangoModelFactory):
    form = SubFactory(FormFactory)
    question = SubFactory(QuestionFactory)
    sort = 0

    class Meta:
        model = models.FormQuestion


class DocumentFactory(DjangoModelFactory):
    form = SubFactory(FormFactory)
    family = None
    meta = {}

    class Meta:
        model = models.Document


class AnswerFactory(DjangoModelFactory):
    question = SubFactory(QuestionFactory)
    document = SubFactory(DocumentFactory)
    value = Faker("name")
    meta = {}

    class Meta:
        model = models.Answer


class AnswerDocumentFactory(DjangoModelFactory):
    answer = SubFactory(AnswerFactory)
    document = SubFactory(DocumentFactory)
    sort = 0

    class Meta:
        model = models.AnswerDocument
