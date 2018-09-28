from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models
from ..form.factories import FormSpecificationFactory, QuestionFactory


class DocumentFactory(DjangoModelFactory):
    form_specification = SubFactory(FormSpecificationFactory)
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
