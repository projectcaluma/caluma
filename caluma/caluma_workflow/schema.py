import itertools

import graphene
from django.db.models import Q
from graphene import relay
from graphene.types import generic
from graphene_django.rest_framework import serializer_converter

from ..caluma_core.filters import (
    CollectionFilterSetFactory,
    DjangoFilterConnectionField,
    DjangoFilterInterfaceConnectionField,
    InterfaceMetaFactory,
)
from ..caluma_core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..caluma_core.types import (
    CountableConnectionBase,
    DjangoObjectType,
    Node,
    enum_type_from_field,
)
from ..caluma_workflow.domain_logic import RedoWorkItemLogic
from . import filters, jexl, models, serializers


class FlowJexl(graphene.String):
    """Flow jexl represents a jexl expression returning task slugs.

    Following transforms can be used:
    * task - return single task
    * tasks - return multiple tasks

    Examples:
    * 'task-slug'|task
    * ['task-slug1', 'task-slug2']|tasks

    """

    pass


class GroupJexl(graphene.String):
    """Group jexl represents a jexl expression returning group names.

    Following transforms can be used:
    * groups - return list of group names

    Examples:
    * ['group-name1', 'group-name2']|groups

    """

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.FlowJexlField, lambda field: FlowJexl
)
serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.GroupJexlField, lambda field: GroupJexl
)


CaseStatus = enum_type_from_field(
    "CaseStatus", models.Case.status, serializer_field=serializers.CaseStatusField
)

WorkItemStatus = enum_type_from_field(
    "WorkItemStatus",
    models.WorkItem.status,
    serializer_field=serializers.WorkItemStatusField,
)


class Task(Node, graphene.Interface):
    id = graphene.ID(required=True)
    created_at = graphene.DateTime(required=True)
    modified_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    slug = graphene.String(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    is_archived = graphene.Boolean(required=True)
    address_groups = GroupJexl()
    control_groups = GroupJexl()
    meta = generic.GenericScalar(required=True)
    is_multiple_instance = graphene.Boolean(required=True)
    continue_async = graphene.Boolean()

    @classmethod
    def resolve_type(cls, instance, info):
        TASK_TYPE = {
            models.Task.TYPE_SIMPLE: SimpleTask,
            models.Task.TYPE_COMPLETE_WORKFLOW_FORM: CompleteWorkflowFormTask,
            models.Task.TYPE_COMPLETE_TASK_FORM: CompleteTaskFormTask,
        }

        return TASK_TYPE[instance.type]

    Meta = InterfaceMetaFactory()


class TaskConnection(CountableConnectionBase):
    class Meta:
        node = Task


class TaskQuerysetMixin(object):
    """Mixin to combine all different task types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Task.get_queryset(queryset, info)


class SimpleTask(TaskQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Task
        exclude = ("task_flows", "work_items", "form", "type")
        use_connection = False
        interfaces = (Task, relay.Node)


class CompleteWorkflowFormTask(TaskQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Task
        exclude = ("task_flows", "work_items", "form", "type")
        use_connection = False
        interfaces = (Task, relay.Node)


class CompleteTaskFormTask(TaskQuerysetMixin, DjangoObjectType):
    form = graphene.Field("caluma.caluma_form.schema.Form", required=True)

    class Meta:
        model = models.Task
        exclude = ("task_flows", "work_items", "type")
        use_connection = False
        interfaces = (Task, relay.Node)


class Flow(DjangoObjectType):
    next = FlowJexl(required=True)
    tasks = graphene.List(Task, required=True)

    def resolve_tasks(self, info, **args):
        return models.Task.objects.filter(pk__in=self.task_flows.values("task"))

    class Meta:
        model = models.Flow
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase
        fields = "__all__"


class Workflow(DjangoObjectType):
    start_tasks = graphene.List(Task, required=True)
    tasks = graphene.List(
        Task, required=True, description="List of tasks referenced in workflow"
    )
    meta = generic.GenericScalar()

    def resolve_tasks(self, info, **args):
        flow_jexl = jexl.FlowJexl()

        next_jexls = self.flows.values_list("next", flat=True)
        jexl_tasks = itertools.chain(
            *[flow_jexl.extract_tasks(next_jexl) for next_jexl in next_jexls]
        )

        return models.Task.objects.filter(
            Q(pk__in=self.start_tasks.all()) | Q(pk__in=jexl_tasks)
        )

    def resolve_start_tasks(self, info, **args):
        return self.start_tasks.all()

    flows = DjangoFilterConnectionField(
        Flow,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.FlowFilterSet,
            orderset_class=filters.FlowOrderSet,
        ),
    )

    class Meta:
        model = models.Workflow
        exclude = ("cases", "task_flows")
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase


class WorkItem(DjangoObjectType):
    task = graphene.Field(Task, required=True)
    meta = generic.GenericScalar()
    assigned_users = graphene.List(graphene.String, required=True)
    controlling_groups = graphene.List(graphene.String, required=True)
    addressed_groups = graphene.List(graphene.String, required=True)
    status = WorkItemStatus(required=True)
    is_redoable = graphene.Boolean(
        description=(
            "This property potentially performs poorly if used in a large set"
            "of entries, as the evaluation of the redoable jexl configuration"
            "cannot be performed on the database level. Please use carefully."
        )
    )

    def resolve_is_redoable(self, *args, **kwargs):
        return (
            self.status != models.WorkItem.STATUS_READY
            and RedoWorkItemLogic.is_work_item_redoable(self)
        )

    class Meta:
        model = models.WorkItem
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase
        fields = "__all__"


class Case(DjangoObjectType):
    work_items = DjangoFilterConnectionField(
        WorkItem,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.WorkItemFilterSet,
            orderset_class=filters.WorkItemOrderSet,
        ),
    )
    family_work_items = DjangoFilterConnectionField(
        WorkItem,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.WorkItemFilterSet,
            orderset_class=filters.WorkItemOrderSet,
        ),
    )
    meta = generic.GenericScalar()
    status = CaseStatus(required=True)

    def resolve_family_work_items(self, info, **args):
        return models.WorkItem.objects.filter(case__family=self.family)

    class Meta:
        model = models.Case
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase
        fields = "__all__"


class SaveWorkflow(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveWorkflowSerializer


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
    """
    Base class of all save task mutations.

    Defined so it is easy to set a permission for all different types
    of tasks.

    See `caluma.permissions.BasePermission` for more details.
    """

    class Meta:
        abstract = True


class SaveSimpleTask(SaveTask):
    class Meta:
        serializer_class = serializers.SaveSimpleTaskSerializer
        return_field_type = Task


class SaveCompleteWorkflowFormTask(SaveTask):
    class Meta:
        serializer_class = serializers.SaveCompleteWorkflowFormTaskSerializer
        return_field_type = Task


class SaveCompleteTaskFormTask(SaveTask):
    class Meta:
        serializer_class = serializers.SaveCompleteTaskFormTaskSerializer
        return_field_type = Task


class SaveCase(Mutation):
    class Input:
        id = graphene.String()

    class Meta:
        serializer_class = serializers.SaveCaseSerializer
        model_operations = ["create", "update"]


class CancelCase(Mutation):
    class Meta:
        serializer_class = serializers.CancelCaseSerializer
        model_operations = ["update"]


class SuspendCase(Mutation):
    class Meta:
        serializer_class = serializers.SuspendCaseSerializer
        model_operations = ["update"]


class ResumeCase(Mutation):
    class Meta:
        serializer_class = serializers.ResumeCaseSerializer
        model_operations = ["update"]


class ReopenCase(Mutation):
    class Input:
        id = graphene.ID(required=True)
        work_items = graphene.List(
            graphene.ID,
            required=True,
            description="List of work item ids to be readied when the case is reopened",
        )

    class Meta:
        serializer_class = serializers.ReopenCaseSerializer
        model_operations = ["update"]


class CompleteWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.CompleteWorkItemSerializer
        model_operations = ["update"]


class SkipWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.SkipWorkItemSerializer
        model_operations = ["update"]


class CancelWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.CancelWorkItemSerializer
        model_operations = ["update"]


class SuspendWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.SuspendWorkItemSerializer
        model_operations = ["update"]


class ResumeWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.ResumeWorkItemSerializer
        model_operations = ["update"]


class RedoWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.WorkItemRedoTaskSerializer
        model_operations = ["update"]


class SaveWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.SaveWorkItemSerializer
        lookup_input_kwarg = "work_item"
        model_operations = ["update"]


class CreateWorkItem(Mutation):
    class Meta:
        serializer_class = serializers.CreateWorkItemSerializer
        model_operations = ["create"]


class Mutation(object):
    save_workflow = SaveWorkflow().Field()
    add_workflow_flow = AddWorkflowFlow().Field()
    remove_flow = RemoveFlow().Field()

    save_simple_task = SaveSimpleTask().Field()
    save_complete_workflow_form_task = SaveCompleteWorkflowFormTask().Field()
    save_complete_task_form_task = SaveCompleteTaskFormTask().Field()

    save_case = SaveCase().Field()
    cancel_case = CancelCase().Field()
    suspend_case = SuspendCase().Field()
    resume_case = ResumeCase().Field()
    reopen_case = ReopenCase().Field()

    complete_work_item = CompleteWorkItem().Field()
    skip_work_item = SkipWorkItem().Field()
    cancel_work_item = CancelWorkItem().Field()
    suspend_work_item = SuspendWorkItem().Field()
    resume_work_item = ResumeWorkItem().Field()
    redo_work_item = RedoWorkItem().Field()
    save_work_item = SaveWorkItem().Field()
    create_work_item = CreateWorkItem().Field()


class Query(object):
    all_workflows = DjangoFilterConnectionField(
        Workflow,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.WorkflowFilterSet,
            orderset_class=filters.WorkflowOrderSet,
        ),
    )
    all_tasks = DjangoFilterInterfaceConnectionField(
        TaskConnection,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.TaskFilterSet,
            orderset_class=filters.TaskOrderSet,
        ),
    )
    all_cases = DjangoFilterConnectionField(
        Case,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.CaseFilterSet,
            orderset_class=filters.CaseOrderSet,
        ),
    )

    all_work_items = DjangoFilterConnectionField(
        WorkItem,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.WorkItemFilterSet,
            orderset_class=filters.WorkItemOrderSet,
        ),
    )
