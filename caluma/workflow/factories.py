from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models
from ..form.factories import FormFactory, FormSpecificationFactory


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
    form_specification = SubFactory(FormSpecificationFactory)

    class Meta:
        model = models.WorkflowSpecification


class FlowFactory(DjangoModelFactory):
    workflow_specification = SubFactory(WorkflowSpecificationFactory)
    task_specification = SubFactory(TaskSpecificationFactory)
    next = Faker("slug")

    class Meta:
        model = models.Flow


class WorkflowFactory(DjangoModelFactory):
    workflow_specification = SubFactory(WorkflowSpecificationFactory)
    status = models.Workflow.STATUS_RUNNING
    form = SubFactory(FormFactory)
    meta = {}

    class Meta:
        model = models.Workflow


class TaskFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    task_specification = SubFactory(TaskSpecificationFactory)
    status = models.Task.STATUS_READY
    meta = {}

    class Meta:
        model = models.Task
