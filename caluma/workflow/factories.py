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
    form = SubFactory(FormFactory)

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
    next = Faker("slug")

    class Meta:
        model = models.Flow


class TaskFlowFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    task = SubFactory(TaskFactory)
    flow = SubFactory(FlowFactory)

    class Meta:
        model = models.TaskFlow


class CaseFactory(DjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    status = models.Case.STATUS_RUNNING
    meta = {}
    document = SubFactory(DocumentFactory)

    class Meta:
        model = models.Case


class WorkItemFactory(DjangoModelFactory):
    case = SubFactory(CaseFactory)
    child_case = SubFactory(CaseFactory)
    task = SubFactory(TaskFactory)
    status = models.WorkItem.STATUS_READY
    document = SubFactory(DocumentFactory)
    meta = {}

    class Meta:
        model = models.WorkItem
