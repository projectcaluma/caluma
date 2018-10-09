import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework import serializer_converter
from graphene_django.types import DjangoObjectType

from . import filters, models, serializers
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin


class FlowJexl(graphene.String):
    """Flow jexl represents a jexl expression returning a task_specification slug."""

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.FlowJexlField, lambda field: FlowJexl
)


class Flow(DjangoObjectType):
    next = FlowJexl(required=True)

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


class TaskSpecification(DjangoObjectType):
    class Meta:
        model = models.TaskSpecification
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


class Workflow(DjangoObjectType):
    class Meta:
        model = models.Workflow
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
        only_fields = (
            "id",
            "created",
            "modified",
            "meta",
            "task_specification",
            "status",
            "workflow",
        )


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


class SaveTaskSpecification(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveTaskSpecificationSerializer


class ArchiveTaskSpecification(SerializerMutation):
    class Meta:
        serializer_class = serializers.ArchiveTaskSpecificationSerializer
        lookup_input_kwarg = "id"


class StartWorkflow(SerializerMutation):
    class Meta:
        serializer_class = serializers.StartWorkflowSerializer
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

    save_task_specification = SaveTaskSpecification().Field()
    archive_task_specification = ArchiveTaskSpecification().Field()

    start_workflow = StartWorkflow().Field()
    complete_work_item = CompleteWorkItem().Field()


class Query(object):
    all_workflow_specifications = DjangoFilterConnectionField(
        WorkflowSpecification, filterset_class=filters.WorkflowSpecificationFilterSet
    )
    all_task_specifications = DjangoFilterConnectionField(
        TaskSpecification, filterset_class=filters.TaskSpecificationFilterSet
    )
    all_workflows = DjangoFilterConnectionField(
        Workflow, filterset_class=filters.WorkflowFilterSet
    )
    all_work_items = DjangoFilterConnectionField(
        WorkItem, filterset_class=filters.WorkItemFilterSet
    )
