from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import models


class Flow(DjangoObjectType):
    class Meta:
        model = models.Flow
        filter_fields = ("task_specification",)
        only_fields = ("task_specification", "next")
        interfaces = (relay.Node,)


class WorkflowSpecification(DjangoObjectType):
    flows = DjangoFilterConnectionField(Flow)

    class Meta:
        model = models.WorkflowSpecification
        filter_fields = ("slug", "name", "description", "is_published", "is_archived")
        interfaces = (relay.Node,)


class TaskSpecification(DjangoObjectType):
    class Meta:
        model = models.TaskSpecification
        filter_fields = ("slug", "name", "description", "type", "is_archived")
        interfaces = (relay.Node,)


class Query(object):
    all_workflow_specifications = DjangoFilterConnectionField(WorkflowSpecification)
    all_task_specifications = DjangoFilterConnectionField(TaskSpecification)
