import graphene
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene.types import ObjectType, generic
from graphene_django.rest_framework import serializer_converter

from caluma.utils import suppressable_visibility_resolver

from ..caluma_core.filters import (
    CollectionFilterSetFactory,
    DjangoFilterConnectionField,
    DjangoFilterInterfaceConnectionField,
    InterfaceMetaFactory,
)
from ..caluma_core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..caluma_core.relay import extract_global_id
from ..caluma_core.types import (
    ConnectionField,
    CountableConnectionBase,
    DjangoObjectType,
    Node,
    enum_type_from_field,
)
from ..caluma_data_source.data_source_handlers import get_data_source_data
from ..caluma_data_source.schema import DataSourceDataConnection
from . import filters, models, serializers
from .format_validators import get_format_validators
from .validators import get_document_validity


def resolve_answer(answer):
    if answer.question.type in [
        models.Question.TYPE_STATIC,
        models.Question.TYPE_ACTION_BUTTON,
    ]:
        raise Exception(
            'Questions of type "static" and "action_button" should never have an answer!'
        )
    return QUESTION_ANSWER_TYPES[answer.question.type]


def resolve_question(question):
    return QUESTION_OBJECT_TYPES[question.type]


class FormDjangoObjectType(DjangoObjectType):
    """
    Django object type with improved `is_type_of`.

    This is needed to resolve our different Answer and Question types.
    """

    @classmethod
    def is_type_of(cls, root, info):
        is_type = super().is_type_of(root, info)
        if is_type:
            if root._meta.model == models.Answer:
                return resolve_answer(root)._meta.name == cls._meta.name
            if root._meta.model == models.Question:
                return resolve_question(root)._meta.name == cls._meta.name
        return is_type

    class Meta:
        abstract = True


class QuestionJexl(graphene.String):
    """Question jexl expression returning boolean.

    Following transforms can be used:
    * `answer`: get answer of document by question slug
    * `mapby`: map list by key. Helpful to work with table answers
      whereas an answer is a list of dicts.
    * `stringify`: JSON stringify
    * `flatten`: flatten list values
    * `min`: get min value in a list
    * `max`: get max value in a list
    * `sum`: sum of a list
    * `round`: round the value
    * `ceil`: round value up
    * `floor`: round value down
    * `debug`: debug output

    Following binary operators can be used:
    * `intersects`: list intersection operator

    Following context is available:
    * `form`: legacy property pointing to the root form (this should not be used anymore)
    * `info.form`: slug of the form this question is attached to
    * `info.formMeta`: meta property of the form this question is attached to
    * `info.parent.form`: parent form slug
    * `info.parent.formMeta`: parent form meta property
    * `info.root.form`: top level form slug
    * `info.root.formMeta`: top level form meta property

    Examples:
    * 'answer' == 'question-slug'|answer
    * 'answer' in 'list-question-slug'|answer
    * 'answer' in 'table-question-slug'|answer|mapby('column-question')
    * 'answer' in 'table-question-slug'|answer|mapby('multiple-choice-question')|flatten
    * 'form-slug' == info.form

    """

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.QuestionJexlField, lambda field: QuestionJexl
)


ButtonAction = enum_type_from_field(
    "ButtonAction",
    choices=models.Question.ACTION_CHOICES,
    serializer_field=serializers.ButtonActionField,
)

ButtonColor = enum_type_from_field(
    "ButtonColor",
    choices=models.Question.COLOR_CHOICES,
    serializer_field=serializers.ButtonColorField,
)


class Question(Node, graphene.Interface):
    id = graphene.ID(required=True)
    created_at = graphene.DateTime(required=True)
    modified_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    modified_by_user = graphene.String()
    modified_by_group = graphene.String()
    slug = graphene.String(required=True)
    label = graphene.String(required=True)
    info_text = graphene.String()
    is_required = QuestionJexl(
        required=True,
        description="Required expression is only evaluated when question is not hidden.",
    )
    is_hidden = QuestionJexl(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = generic.GenericScalar(required=True)
    forms = DjangoFilterConnectionField(
        "caluma.caluma_form.schema.Form",
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.FormFilterSet, orderset_class=filters.FormOrderSet
        ),
    )
    source = graphene.Field("caluma.caluma_form.schema.Question")

    resolve_source = suppressable_visibility_resolver()

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return (
            queryset.select_related("sub_form", "row_form")
            .order_by("-formquestion__sort")
            .distinct()
        )

    @classmethod
    def resolve_type(cls, instance, info):
        return resolve_question(instance)

    Meta = InterfaceMetaFactory()


class Option(FormDjangoObjectType):
    meta = generic.GenericScalar()
    is_hidden = QuestionJexl(required=True)

    resolve_source = suppressable_visibility_resolver()

    class Meta:
        model = models.Option
        interfaces = (relay.Node,)
        exclude = ("questions",)
        connection_class = CountableConnectionBase

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return queryset.order_by("-questionoption__sort")


class QuestionConnection(CountableConnectionBase):
    class Meta:
        node = Question


class QuestionQuerysetMixin(object):
    """Mixin to combine all different question types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Question.get_queryset(queryset, info)


class FormatValidator(ObjectType):
    slug = graphene.String(required=True)
    name = graphene.String(required=True)
    regex = graphene.String(required=False)
    allowed_question_types = graphene.List(graphene.String)


class FormatValidatorConnection(CountableConnectionBase):
    class Meta:
        node = FormatValidator


class FormatValidatorMixin:
    format_validators = ConnectionField(FormatValidatorConnection)

    def resolve_format_validators(self, info, *args, **kwargs):
        return get_format_validators(include=self.format_validators)


class TextQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    min_length = graphene.Int()
    max_length = graphene.Int()
    placeholder = graphene.String()
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.StringAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TextareaQuestion(
    FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType
):
    min_length = graphene.Int()
    max_length = graphene.Int()
    placeholder = graphene.String()
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.StringAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DateQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.DateAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class ChoiceQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    options = DjangoFilterConnectionField(
        Option,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.OptionFilterSet,
            orderset_class=filters.OptionOrderSet,
        ),
    )
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.StringAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class MultipleChoiceQuestion(
    FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType
):
    options = DjangoFilterConnectionField(
        Option,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.OptionFilterSet,
            orderset_class=filters.OptionOrderSet,
        ),
    )
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.ListAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicQuestion(graphene.Interface):
    options = ConnectionField(
        DataSourceDataConnection,
        context=graphene.JSONString(
            description="JSON object passed as context to the data source"
        ),
    )
    data_source = graphene.String(required=True)
    hint_text = graphene.String()

    def resolve_options(self, info, context=None, *args, **kwargs):
        return get_data_source_data(info.context.user, self.data_source, self, context)


class DynamicChoiceQuestion(
    FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType
):
    hint_text = graphene.String()

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, DynamicQuestion, graphene.Node)


class DynamicMultipleChoiceQuestion(
    FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType
):
    hint_text = graphene.String()

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, DynamicQuestion, graphene.Node)


class DynamicOption(DjangoObjectType):
    question = graphene.Field(
        "caluma.caluma_form.schema.DynamicQuestion", required=True
    )

    class Meta:
        model = models.DynamicOption
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase
        fields = "__all__"


class IntegerQuestion(
    FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType
):
    max_value = graphene.Int()
    min_value = graphene.Int()
    placeholder = graphene.String()
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.IntegerAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FloatQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()
    step = graphene.Float()
    placeholder = graphene.String()
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.FloatAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TableQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    hint_text = graphene.String()
    default_answer = graphene.Field("caluma.caluma_form.schema.TableAnswer")

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FormQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "placeholder",
            "hint_text",
            "static_content",
            "format_validators",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FilesQuestion(FormatValidatorMixin, QuestionQuerysetMixin, FormDjangoObjectType):
    hint_text = graphene.String()

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class StaticQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    is_required = QuestionJexl(
        required=True,
        description="Required expression is only evaluated when question is not hidden."
        " This should not be used for `StaticQuestion`, because it can never be satisfied.",
    )

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "hint_text",
            "format_validators",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class CalculatedFloatQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    hint_text = graphene.String()

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
            "format_validators",
            "dynamicoption_set",
            "default_answer",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class ActionButtonQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    action = ButtonAction(required=True)
    color = ButtonColor(required=True)
    validate_on_enter = graphene.Boolean(required=True)
    show_validation = graphene.Boolean(required=True)

    class Meta:
        model = models.Question
        exclude = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "hint_text",
            "static_content",
            "format_validators",
            "dynamicoption_set",
            "default_answer",
            "calc_expression",
            "calc_dependents",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class Form(FormDjangoObjectType):
    questions = DjangoFilterInterfaceConnectionField(
        QuestionConnection,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.QuestionFilterSet,
            orderset_class=filters.QuestionOrderSet,
        ),
    )
    meta = generic.GenericScalar()

    resolve_source = suppressable_visibility_resolver()

    class Meta:
        model = models.Form
        interfaces = (relay.Node,)
        exclude = ("workflows", "tasks")
        connection_class = CountableConnectionBase


class SaveForm(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveFormSerializer


class CopyForm(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.CopyFormSerializer
        model_operations = ["create"]


class AddFormQuestion(Mutation):
    """Add question at the end of form."""

    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.AddFormQuestionSerializer


class RemoveFormQuestion(Mutation):
    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.RemoveFormQuestionSerializer


class ReorderFormQuestions(Mutation):
    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.ReorderFormQuestionsSerializer


class CopyQuestion(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.CopyQuestionSerializer
        return_field_type = Question
        model_operations = ["create"]


class SaveQuestion(UserDefinedPrimaryKeyMixin, Mutation):
    """
    Base class of all save question mutations.

    Defined so it is easy to set a permission for all different types
    of questions.

    See `caluma.permissions.BasePermission` for more details.
    """

    class Meta:
        abstract = True


class SaveTextQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveTextQuestionSerializer
        return_field_type = Question


class SaveTextareaQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveTextareaQuestionSerializer
        return_field_type = Question


class SaveDateQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveDateQuestionSerializer
        return_field_type = Question


class SaveChoiceQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveChoiceQuestionSerializer
        return_field_type = Question


class SaveMultipleChoiceQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveMultipleChoiceQuestionSerializer
        return_field_type = Question


class SaveDynamicChoiceQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveDynamicChoiceQuestionSerializer
        return_field_type = Question


class SaveDynamicMultipleChoiceQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveDynamicMultipleChoiceQuestionSerializer
        return_field_type = Question


class SaveIntegerQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveIntegerQuestionSerializer
        return_field_type = Question


class SaveFloatQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveFloatQuestionSerializer
        return_field_type = Question


class SaveTableQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveTableQuestionSerializer
        return_field_type = Question


class SaveFormQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveFormQuestionSerializer
        return_field_type = Question


class SaveFilesQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveFileQuestionSerializer
        return_field_type = Question


class SaveStaticQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveStaticQuestionSerializer
        return_field_type = Question


class SaveCalculatedFloatQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveCalculatedFloatQuestionSerializer
        return_field_type = Question


class SaveActionButtonQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveActionButtonQuestionSerializer
        return_field_type = Question


class SaveOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveOptionSerializer


class CopyOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.CopyOptionSerializer
        model_operations = ["create"]


class Answer(Node, graphene.Interface):
    id = graphene.ID()
    created_at = graphene.DateTime(required=True)
    modified_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    modified_by_user = graphene.String()
    modified_by_group = graphene.String()
    question = graphene.Field(Question, required=True)
    meta = generic.GenericScalar(required=True)

    resolve_question = suppressable_visibility_resolver()

    @classmethod
    def resolve_type(cls, instance, info):
        return resolve_answer(instance)

    Meta = InterfaceMetaFactory()


class AnswerQuerysetMixin(object):
    """Mixin to combine all different answer types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Answer.get_queryset(queryset, info)


class IntegerAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.Int()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "files", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FloatAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.Float()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "files", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class DateAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.types.datetime.Date()

    def resolve_value(self, info, **args):
        return self.date

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "files")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class SelectedOption(ObjectType):
    label = graphene.String(required=True)
    slug = graphene.String(required=True)


class SelectedOptionConnection(CountableConnectionBase):
    class Meta:
        node = SelectedOption


class StringAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.String()
    selected_option = graphene.Field(SelectedOption)

    def resolve_selected_option(self, info, **args):
        selected_options = self.selected_options
        return selected_options[0] if selected_options else None

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "files", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class ListAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.List(graphene.String)
    selected_options = ConnectionField(SelectedOptionConnection)

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "files", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class AnswerConnection(CountableConnectionBase):
    class Meta:
        node = Answer


class Document(FormDjangoObjectType):
    answers = DjangoFilterInterfaceConnectionField(
        AnswerConnection,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.AnswerFilterSet,
            orderset_class=filters.AnswerOrderSet,
        ),
    )
    meta = generic.GenericScalar()
    modified_content_at = graphene.DateTime()
    modified_content_by_user = graphene.String()
    modified_content_by_group = graphene.String()

    resolve_form = suppressable_visibility_resolver()
    resolve_case = suppressable_visibility_resolver()
    resolve_source = suppressable_visibility_resolver()
    resolve_work_item = suppressable_visibility_resolver()

    class Meta:
        model = models.Document
        exclude = ("family", "dynamicoption_set")
        interfaces = (graphene.Node,)
        connection_class = CountableConnectionBase


class TableAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.List(Document)

    def resolve_value(self, info, **args):
        return self.documents.order_by("-answerdocument__sort")

    class Meta:
        model = models.Answer
        exclude = ("documents", "files", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class File(FormDjangoObjectType):
    name = graphene.String(required=True)
    upload_url = graphene.String()
    download_url = graphene.String()
    metadata = generic.GenericScalar()

    class Meta:
        model = models.File
        interfaces = (relay.Node,)
        fields = "__all__"


class FilesAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.List(File, required=True)

    def resolve_value(self, info, **args):
        return self.files.all()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "date", "files")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class SaveDocument(Mutation):
    class Input:
        id = graphene.String()

    class Meta:
        serializer_class = serializers.DocumentSerializer
        model_operations = ["create", "update"]


class CopyDocument(Mutation):
    class Meta:
        serializer_class = serializers.CopyDocumentSerializer
        model_operations = ["create"]


class SaveDocumentAnswer(Mutation):
    @classmethod
    def get_object(cls, root, info, queryset, **input):
        question_id = extract_global_id(input["question"])
        document_id = extract_global_id(input["document"])
        instance = models.Answer.objects.filter(
            question=question_id, document=document_id
        ).first()
        return instance

    class Meta:
        abstract = True


class SaveDocumentStringAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentStringAnswerSerializer
        return_field_type = Answer


class SaveDocumentListAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentListAnswerSerializer
        return_field_type = Answer


class SaveDocumentIntegerAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentIntegerAnswerSerializer
        return_field_type = Answer


class SaveDocumentFloatAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentFloatAnswerSerializer
        return_field_type = Answer


class SaveDocumentDateAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentDateAnswerSerializer
        return_field_type = Answer


class SaveDocumentTableAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentTableAnswerSerializer
        return_field_type = Answer


class SaveFile(graphene.InputObjectType):
    id = graphene.String()
    name = graphene.String()


class SaveDocumentFilesAnswer(SaveDocumentAnswer):
    class Input:
        value = graphene.List(SaveFile, required=False)

    class Meta:
        serializer_class = serializers.SaveDocumentFilesAnswerSerializer
        return_field_type = Answer


class SaveDefaultAnswer(Mutation):
    @classmethod
    def get_object(cls, root, info, queryset, **input):
        question_id = extract_global_id(input["question"])
        instance = models.Question.objects.get(pk=question_id).default_answer
        return instance

    class Meta:
        abstract = True


class SaveDefaultStringAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultStringAnswerSerializer
        return_field_type = Answer


class SaveDefaultListAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultListAnswerSerializer
        return_field_type = Answer


class SaveDefaultIntegerAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultIntegerAnswerSerializer
        return_field_type = Answer


class SaveDefaultFloatAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultFloatAnswerSerializer
        return_field_type = Answer


class SaveDefaultDateAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultDateAnswerSerializer
        return_field_type = Answer


class SaveDefaultTableAnswer(SaveDefaultAnswer):
    class Meta:
        serializer_class = serializers.SaveDefaultTableAnswerSerializer
        return_field_type = Answer


class RemoveAnswer(Mutation):
    class Meta:
        lookup_input_kwarg = "answer"
        serializer_class = serializers.RemoveAnswerSerializer
        return_field_type = Answer


class RemoveDefaultAnswer(Mutation):
    class Meta:
        lookup_input_kwarg = "question"
        serializer_class = serializers.RemoveDefaultAnswerSerializer
        return_field_type = Question


class RemoveDocument(Mutation):
    class Meta:
        lookup_input_kwarg = "document"
        serializer_class = serializers.RemoveDocumentSerializer


class Mutation(object):
    save_form = SaveForm().Field()
    copy_form = CopyForm().Field()
    add_form_question = AddFormQuestion().Field()
    remove_form_question = RemoveFormQuestion().Field()
    reorder_form_questions = ReorderFormQuestions().Field()

    save_option = SaveOption().Field()
    copy_option = CopyOption().Field()

    copy_question = CopyQuestion().Field()
    save_text_question = SaveTextQuestion().Field()
    save_textarea_question = SaveTextareaQuestion().Field()
    save_date_question = SaveDateQuestion().Field()
    save_choice_question = SaveChoiceQuestion().Field()
    save_multiple_choice_question = SaveMultipleChoiceQuestion().Field()
    save_dynamic_choice_question = SaveDynamicChoiceQuestion().Field()
    save_dynamic_multiple_choice_question = SaveDynamicMultipleChoiceQuestion().Field()
    save_float_question = SaveFloatQuestion().Field()
    save_integer_question = SaveIntegerQuestion().Field()
    save_table_question = SaveTableQuestion().Field()
    save_form_question = SaveFormQuestion().Field()
    save_files_question = SaveFilesQuestion().Field()
    save_static_question = SaveStaticQuestion().Field()
    save_calculated_float_question = SaveCalculatedFloatQuestion().Field()
    save_action_button_question = SaveActionButtonQuestion().Field()

    copy_document = CopyDocument().Field()
    save_document = SaveDocument().Field()
    save_document_string_answer = SaveDocumentStringAnswer().Field()
    save_document_integer_answer = SaveDocumentIntegerAnswer().Field()
    save_document_float_answer = SaveDocumentFloatAnswer().Field()
    save_document_date_answer = SaveDocumentDateAnswer().Field()
    save_document_list_answer = SaveDocumentListAnswer().Field()
    save_document_table_answer = SaveDocumentTableAnswer().Field()
    save_document_files_answer = SaveDocumentFilesAnswer().Field()

    save_default_string_answer = SaveDefaultStringAnswer().Field()
    save_default_integer_answer = SaveDefaultIntegerAnswer().Field()
    save_default_float_answer = SaveDefaultFloatAnswer().Field()
    save_default_date_answer = SaveDefaultDateAnswer().Field()
    save_default_list_answer = SaveDefaultListAnswer().Field()
    save_default_table_answer = SaveDefaultTableAnswer().Field()

    remove_answer = RemoveAnswer().Field()
    remove_default_answer = RemoveDefaultAnswer().Field()
    remove_document = RemoveDocument().Field()


class ValidationEntry(ObjectType):
    slug = graphene.String(required=True)
    error_msg = graphene.String(required=True)


class ValidationResult(ObjectType):
    id = graphene.ID()
    id.__doc__ = "References the document ID"

    is_valid = graphene.Boolean()
    errors = graphene.List(ValidationEntry)


class DocumentValidityConnection(CountableConnectionBase):
    class Meta:
        node = ValidationResult


def validate_document(info, document_global_id, **kwargs):
    document_id = extract_global_id(document_global_id)

    document_qs = Document.get_queryset(models.Document.objects.all(), info)

    document = get_object_or_404(document_qs, pk=document_id)
    result = get_document_validity(document, info.context.user, **kwargs)

    errors = result.pop("errors")
    result = ValidationResult(
        **result, errors=[ValidationEntry(**err) for err in errors]
    )

    return [result]


class Query:
    all_forms = DjangoFilterConnectionField(
        Form,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.FormFilterSet,
            orderset_class=filters.FormOrderSet,
        ),
    )
    all_questions = DjangoFilterInterfaceConnectionField(
        QuestionConnection,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.QuestionFilterSet,
            orderset_class=filters.QuestionOrderSet,
        ),
    )
    all_documents = DjangoFilterConnectionField(
        Document,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.DocumentFilterSet,
            orderset_class=filters.DocumentOrderSet,
        ),
    )
    all_format_validators = ConnectionField(FormatValidatorConnection)
    all_used_dynamic_options = DjangoFilterConnectionField(
        DynamicOption,
        filterset_class=CollectionFilterSetFactory(
            filterset_class=filters.DynamicOptionFilterSet,
            orderset_class=filters.DynamicOptionOrderSet,
        ),
    )

    document_validity = ConnectionField(
        DocumentValidityConnection,
        id=graphene.ID(required=True),
        data_source_context=graphene.JSONString(),
    )

    def resolve_all_format_validators(self, info, **kwargs):
        return get_format_validators()

    def resolve_document_validity(self, info, id, **kwargs):
        return validate_document(info, id, **kwargs)


QUESTION_ANSWER_TYPES = {
    models.Question.TYPE_MULTIPLE_CHOICE: ListAnswer,
    models.Question.TYPE_INTEGER: IntegerAnswer,
    models.Question.TYPE_FLOAT: FloatAnswer,
    models.Question.TYPE_DATE: DateAnswer,
    models.Question.TYPE_CHOICE: StringAnswer,
    models.Question.TYPE_TEXTAREA: StringAnswer,
    models.Question.TYPE_TEXT: StringAnswer,
    models.Question.TYPE_TABLE: TableAnswer,
    models.Question.TYPE_FILES: FilesAnswer,
    models.Question.TYPE_DYNAMIC_CHOICE: StringAnswer,
    models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: ListAnswer,
    models.Question.TYPE_CALCULATED_FLOAT: FloatAnswer,
}

QUESTION_OBJECT_TYPES = {
    models.Question.TYPE_TEXT: TextQuestion,
    models.Question.TYPE_FLOAT: FloatQuestion,
    models.Question.TYPE_CHOICE: ChoiceQuestion,
    models.Question.TYPE_INTEGER: IntegerQuestion,
    models.Question.TYPE_MULTIPLE_CHOICE: MultipleChoiceQuestion,
    models.Question.TYPE_DYNAMIC_CHOICE: DynamicChoiceQuestion,
    models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: DynamicMultipleChoiceQuestion,
    models.Question.TYPE_TEXTAREA: TextareaQuestion,
    models.Question.TYPE_DATE: DateQuestion,
    models.Question.TYPE_TABLE: TableQuestion,
    models.Question.TYPE_FORM: FormQuestion,
    models.Question.TYPE_FILES: FilesQuestion,
    models.Question.TYPE_STATIC: StaticQuestion,
    models.Question.TYPE_CALCULATED_FLOAT: CalculatedFloatQuestion,
    models.Question.TYPE_ACTION_BUTTON: ActionButtonQuestion,
}
