from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models


class TaskSpecificationFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.TaskSpecification.TYPE_CHOICES)
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_archived = False

    class Meta:
        model = models.TaskSpecification


class WorkflowSpecificationFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False
    start = SubFactory(TaskSpecificationFactory)

    class Meta:
        model = models.WorkflowSpecification


class FlowFactory(DjangoModelFactory):
    workflow_specification = SubFactory(WorkflowSpecificationFactory)
    task_specification = SubFactory(TaskSpecificationFactory)
    next = Faker("slug")

    class Meta:
        model = models.Flow
