import graphene
from graphene import relay
from graphene_django.rest_framework import serializer_converter

from . import filters, models, serializers
from ..core.filters import DjangoFilterConnectionField
from ..core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..core.types import DjangoObjectType


class FlowJexl(graphene.String):
    """Flow jexl represents a jexl expression returning a task slug."""

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.FlowJexlField, lambda field: FlowJexl
)


class Task(DjangoObjectType):
    class Meta:
        model = models.Task
        exclude_fields = ("task_flows", "work_items")
        interfaces = (relay.Node,)


class Flow(DjangoObjectType):
    next = FlowJexl(required=True)
    tasks = graphene.List(Task, required=True)

    def resolve_tasks(self, info, **args):
        return models.Task.objects.filter(pk__in=self.task_flows.values("task"))

    class Meta:
        model = models.Flow
        only_fields = ("tasks", "next")
        interfaces = (relay.Node,)


class Workflow(DjangoObjectType):
    flows = DjangoFilterConnectionField(Flow, filterset_class=filters.FlowFilterSet)

    def resolve_flows(self, info, **args):
        return models.Flow.objects.filter(pk__in=self.task_flows.values("flow"))

    class Meta:
        model = models.Workflow
        filter_fields = ("slug", "name", "description", "is_published", "is_archived")
        exclude_fields = ("cases", "task_flows")
        interfaces = (relay.Node,)


class Case(DjangoObjectType):
    class Meta:
        model = models.Case
        interfaces = (relay.Node,)


class WorkItem(DjangoObjectType):
    class Meta:
        model = models.WorkItem
        interfaces = (relay.Node,)


class SaveWorkflow(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveWorkflowSerializer


class PublishWorkflow(Mutation):
    class Meta:
        serializer_class = serializers.PublishWorkflowSerializer
        lookup_input_kwarg = "id"


class ArchiveWorkflow(Mutation):
    class Meta:
        serializer_class = serializers.ArchiveWorkflowSerializer
        lookup_input_kwarg = "id"


class AddWorkflowFlow(Mutation):
    class Meta:
        serializer_class = serializers.AddWorkflowFlowSerializer
        lookup_input_kwarg = "workflow"


class RemoveFlow(Mutation):
    class Meta:
        lookup_input_kwarg = "flow"
        serializer_class = serializers.RemoveFlowSerializer
        model_operations = ["update"]


class SaveTask(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveTaskSerializer


class ArchiveTask(Mutation):
    class Meta:
        serializer_class = serializers.ArchiveTaskSerializer
        lookup_input_kwarg = "id"


class StartCase(Mutation):
    class Meta:
        serializer_class = serializers.StartCaseSerializer
        model_operations = ["create"]


class CancelCase(Mutation):
    class Meta:
        serializer_class = serializers.CancelCaseSerializer
        model_operations = ["update"]


class CompleteWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.CompleteWorkItemSerializer
        model_operations = ["update"]


class Mutation(object):
    save_workflow = SaveWorkflow().Field()
    publish_workflow = PublishWorkflow().Field()
    archive_workflow = ArchiveWorkflow().Field()
    add_workflow_flow = AddWorkflowFlow().Field()
    remove_flow = RemoveFlow().Field()

    save_task = SaveTask().Field()
    archive_task = ArchiveTask().Field()

    start_case = StartCase().Field()
    cancel_case = CancelCase().Field()
    complete_work_item = CompleteWorkItem().Field()


class Query(object):
    all_workflows = DjangoFilterConnectionField(
        Workflow, filterset_class=filters.WorkflowFilterSet
    )
    all_tasks = DjangoFilterConnectionField(Task, filterset_class=filters.TaskFilterSet)
    all_cases = DjangoFilterConnectionField(Case, filterset_class=filters.CaseFilterSet)
    all_work_items = DjangoFilterConnectionField(
        WorkItem, filterset_class=filters.WorkItemFilterSet
    )
