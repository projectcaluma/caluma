from factory import Faker, SubFactory
from factory.django import DjangoModelFactory as FactoryDjangoModelFactory

from ..caluma_core.factories import DjangoModelFactory
from ..caluma_form.factories import DocumentFactory, FormFactory
from . import models


class TaskFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=models.Task.TYPE_CHOICES)
    address_groups = None
    control_groups = None
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_archived = False
    form = SubFactory(FormFactory)
    lead_time = None
    is_multiple_instance = False

    class Meta:
        model = models.Task


class WorkflowFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False
    allow_all_forms = False

    class Meta:
        model = models.Workflow


class WorkflowStartTasksFactory(FactoryDjangoModelFactory):
    workflow = SubFactory(WorkflowFactory)
    task = SubFactory(TaskFactory)

    class Meta:
        model = models.Workflow.start_tasks.through


class WorkflowAllowFormsFactory(FactoryDjangoModelFactory):
    form = SubFactory(FormFactory)
    workflow = SubFactory(WorkflowFactory)

    class Meta:
        model = models.Workflow.allow_forms.through


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
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    closed_at = None
    closed_by_user = None
    closed_by_group = None
    deadline = None
    status = models.WorkItem.STATUS_READY
    meta = {}
    addressed_groups = []
    controlling_groups = []
    assigned_users = []
    task = SubFactory(TaskFactory)
    case = SubFactory(CaseFactory)
    child_case = SubFactory(CaseFactory)
    document = SubFactory(DocumentFactory)
    previous_work_item = None

    class Meta:
        model = models.WorkItem
