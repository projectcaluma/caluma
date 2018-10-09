from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models


class TaskFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.Task.TYPE_CHOICES)
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_archived = False

    class Meta:
        model = models.Task


class WorkflowSpecificationFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False
    start = SubFactory(TaskFactory)

    class Meta:
        model = models.WorkflowSpecification


class FlowFactory(DjangoModelFactory):
    workflow_specification = SubFactory(WorkflowSpecificationFactory)
    task = SubFactory(TaskFactory)
    next = Faker("slug")

    class Meta:
        model = models.Flow


class WorkflowFactory(DjangoModelFactory):
    workflow_specification = SubFactory(WorkflowSpecificationFactory)
    status = Faker("word", ext_word_list=models.Workflow.STATUS_CHOICES)
    meta = {}

    class Meta:
        model = models.Workflow


class WorkItemFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    task = SubFactory(TaskFactory)
    status = Faker("word", ext_word_list=models.WorkItem.STATUS_CHOICES)
    meta = {}

    class Meta:
        model = models.WorkItem
