from factory import Faker, SubFactory

from . import models
from ..core.factories import DjangoModelFactory
from ..form.factories import DocumentFactory, FormFactory


class TaskFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.Task.TYPE_CHOICES)
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_archived = False

    class Meta:
        model = models.Task


class WorkflowFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False
    start = SubFactory(TaskFactory)
    form = SubFactory(FormFactory)

    class Meta:
        model = models.Workflow


class FlowFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    task = SubFactory(TaskFactory)
    next = Faker("slug")

    class Meta:
        model = models.Flow


class CaseFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    status = models.Case.STATUS_RUNNING
    meta = {}
    document = SubFactory(DocumentFactory)

    class Meta:
        model = models.Case


class WorkItemFactory(DjangoModelFactory):
    case = SubFactory(CaseFactory)
    task = SubFactory(TaskFactory)
    status = models.WorkItem.STATUS_READY
    meta = {}

    class Meta:
        model = models.WorkItem
