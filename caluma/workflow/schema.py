import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework import serializer_converter
from graphene_django.types import DjangoObjectType

from . import filters, models, serializers
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin


class FlowJexl(graphene.String):
    """Flow jexl represents a jexl expression returning a task slug."""

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.FlowJexlField, lambda field: FlowJexl
)


class Flow(DjangoObjectType):
    next = FlowJexl(required=True)

    class Meta:
        model = models.Flow
        filter_fields = ("task",)
        only_fields = ("task", "next")
        interfaces = (relay.Node,)


class WorkflowSpecification(DjangoObjectType):
    flows = DjangoFilterConnectionField(Flow)

    class Meta:
        model = models.WorkflowSpecification
        filter_fields = ("slug", "name", "description", "is_published", "is_archived")
        only_fields = (
            "created",
            "modified",
            "slug",
            "name",
            "description",
            "meta",
            "is_published",
            "is_archived",
            "start",
        )
        interfaces = (relay.Node,)


class Task(DjangoObjectType):
    class Meta:
        model = models.Task
        interfaces = (relay.Node,)
        only_fields = (
            "created",
            "modified",
            "slug",
            "name",
            "description",
            "type",
            "meta",
            "is_archived",
        )


class Case(DjangoObjectType):
    class Meta:
        model = models.Case
        interfaces = (relay.Node,)
        only_fields = (
            "id",
            "created",
            "modified",
            "meta",
            "workflow_specification",
            "status",
            "work_items",
        )


class WorkItem(DjangoObjectType):
    class Meta:
        model = models.WorkItem
        interfaces = (relay.Node,)
        only_fields = ("id", "created", "modified", "meta", "task", "status", "case")


class SaveWorkflowSpecification(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveWorkflowSpecificationSerializer


class PublishWorkflowSpecification(SerializerMutation):
    class Meta:
        serializer_class = serializers.PublishWorkflowSpecificationSerializer
        lookup_input_kwarg = "id"


class ArchiveWorkflowSpecification(SerializerMutation):
    class Meta:
        serializer_class = serializers.ArchiveWorkflowSpecificationSerializer
        lookup_input_kwarg = "id"


class AddWorkflowSpecificationFlow(SerializerMutation):
    class Meta:
        serializer_class = serializers.AddWorkflowSpecificationFlowSerializer
        lookup_input_kwarg = "workflow_specification"


class RemoveWorkflowSpecificationFlow(SerializerMutation):
    class Meta:
        serializer_class = serializers.RemoveWorkflowSpecificationFlowSerializer
        lookup_input_kwarg = "workflow_specification"


class SaveTask(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveTaskSerializer


class ArchiveTask(SerializerMutation):
    class Meta:
        serializer_class = serializers.ArchiveTaskSerializer
        lookup_input_kwarg = "id"


class StartCase(SerializerMutation):
    class Meta:
        serializer_class = serializers.StartCaseSerializer
        model_operations = ["create"]


class CompleteWorkItem(SerializerMutation):
    class Meta:
        serializer_class = serializers.CompleteWorkItemSerializer
        model_operations = ["update"]


class Mutation(object):
    save_workflow_specification = SaveWorkflowSpecification().Field()
    publish_workflow_specification = PublishWorkflowSpecification().Field()
    archive_workflow_specification = ArchiveWorkflowSpecification().Field()
    add_workflow_specification_flow = AddWorkflowSpecificationFlow().Field()
    remove_workflow_specification_flow = RemoveWorkflowSpecificationFlow().Field()

    save_task = SaveTask().Field()
    archive_task = ArchiveTask().Field()

    start_case = StartCase().Field()
    complete_work_item = CompleteWorkItem().Field()


class Query(object):
    all_workflow_specifications = DjangoFilterConnectionField(
        WorkflowSpecification, filterset_class=filters.WorkflowSpecificationFilterSet
    )
    all_tasks = DjangoFilterConnectionField(Task, filterset_class=filters.TaskFilterSet)
    all_cases = DjangoFilterConnectionField(Case, filterset_class=filters.CaseFilterSet)
    all_work_items = DjangoFilterConnectionField(
        WorkItem, filterset_class=filters.WorkItemFilterSet
    )
