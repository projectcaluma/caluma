import graphene
from graphene import ConnectionField, relay
from graphene.types import generic
from graphene_django.rest_framework import serializer_converter

from ..core.filters import DjangoFilterConnectionField, DjangoFilterSetConnectionField
from ..core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..core.relay import extract_global_id
from ..core.types import DjangoObjectType, Node
from ..data_source.data_source_handlers import get_data_source_data
from ..data_source.schema import DataSourceDataConnection
from . import filters, models, serializers


class QuestionJexl(graphene.String):
    """Question jexl expression returning boolean.

    Following transform can be used:
    * answer - access answer of document by question slug
    * mapby - map list by key. Helpful to work with table answers
      whereas an answer is a list of dicts.

    Examples:
    * 'answer' == 'question-slug'|answer
    * 'answer' in 'list-question-slug'|answer
    * 'answer' in 'table-question-slug'|answer|mapby('column-question')

    """

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.QuestionJexlField, lambda field: QuestionJexl
)


class Question(Node, graphene.Interface):
    id = graphene.ID(required=True)
    created_at = graphene.DateTime(required=True)
    modified_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    slug = graphene.String(required=True)
    label = graphene.String(required=True)
    info_text = graphene.String()
    is_required = QuestionJexl(required=True)
    is_hidden = QuestionJexl(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = generic.GenericScalar(required=True)
    forms = DjangoFilterConnectionField(
        "caluma.form.schema.Form", filterset_class=filters.FormFilterSet
    )
    source = graphene.Field("caluma.form.schema.Question")

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return queryset.order_by("-formquestion__sort")

    @classmethod
    def resolve_type(cls, instance, info):
        QUESTION_OBJECT_TYPE = {
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
            models.Question.TYPE_FILE: FileQuestion,
            models.Question.TYPE_STATIC: StaticQuestion,
        }

        return QUESTION_OBJECT_TYPE[instance.type]


class Option(DjangoObjectType):
    meta = generic.GenericScalar()

    class Meta:
        model = models.Option
        interfaces = (relay.Node,)
        exclude_fields = ("questions",)

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return queryset.order_by("-questionoption__sort")


class QuestionConnection(graphene.Connection):
    class Meta:
        node = Question


class QuestionQuerysetMixin(object):
    """Mixin to combine all different question types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Question.get_queryset(queryset, info)


class TextQuestion(QuestionQuerysetMixin, DjangoObjectType):
    max_length = graphene.Int()
    placeholder = graphene.String()

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TextareaQuestion(QuestionQuerysetMixin, DjangoObjectType):
    max_length = graphene.Int()
    placeholder = graphene.String()

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DateQuestion(QuestionQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class ChoiceQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class MultipleChoiceQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicChoiceQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = ConnectionField(DataSourceDataConnection)
    data_source = graphene.String(required=True)

    def resolve_options(self, info, *args):
        return get_data_source_data(info, self.data_source)

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicMultipleChoiceQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = ConnectionField(DataSourceDataConnection)
    data_source = graphene.String(required=True)

    def resolve_options(self, info, *args):
        return get_data_source_data(info, self.data_source)

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class IntegerQuestion(QuestionQuerysetMixin, DjangoObjectType):
    max_value = graphene.Int()
    min_value = graphene.Int()
    placeholder = graphene.String()

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FloatQuestion(QuestionQuerysetMixin, DjangoObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()
    placeholder = graphene.String()

    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TableQuestion(QuestionQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FormQuestion(QuestionQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FileQuestion(QuestionQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "data_source",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "static_content",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class StaticQuestion(QuestionQuerysetMixin, DjangoObjectType):
    class Meta:
        model = models.Question
        exclude_fields = (
            "type",
            "configuration",
            "options",
            "answers",
            "row_form",
            "sub_form",
            "placeholder",
            "is_required",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class Form(DjangoObjectType):
    questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
    meta = generic.GenericScalar()

    class Meta:
        model = models.Form
        interfaces = (relay.Node,)
        exclude_fields = ("workflows", "tasks")


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


class SaveFileQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveFileQuestionSerializer
        return_field_type = Question


class SaveStaticQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveStaticQuestionSerializer
        return_field_type = Question


class SaveOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveOptionSerializer


class CopyOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.CopyOptionSerializer
        model_operations = ["create"]


class RemoveOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        lookup_input_kwarg = "option"
        serializer_class = serializers.RemoveOptionSerializer
        return_field_name = False
        model_operations = ["update"]


class Answer(Node, graphene.Interface):
    id = graphene.ID()
    created_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    modified_at = graphene.DateTime(required=True)
    question = graphene.Field(Question, required=True)
    meta = generic.GenericScalar(required=True)

    @classmethod
    def resolve_type(cls, instance, info):
        ANSWER_TYPE = {
            list: ListAnswer,
            str: StringAnswer,
            float: FloatAnswer,
            int: IntegerAnswer,
        }

        if instance.value is None:
            ANSWER_QUESTION_TYPE = {
                models.Question.TYPE_FORM: FormAnswer,
                models.Question.TYPE_TABLE: TableAnswer,
                models.Question.TYPE_FILE: FileAnswer,
                models.Question.TYPE_DATE: DateAnswer,
            }
            return ANSWER_QUESTION_TYPE[instance.question.type]

        return ANSWER_TYPE[type(instance.value)]


class AnswerQuerysetMixin(object):
    """Mixin to combine all different answer types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Answer.get_queryset(queryset, info)


class IntegerAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.Int(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FloatAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.Float(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class DateAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.types.datetime.Date(required=True)

    def resolve_value(self, info, **args):
        return self.date

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "file")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class StringAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.String(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class ListAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.List(graphene.String, required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class AnswerConnection(graphene.Connection):
    class Meta:
        node = Answer


class Document(DjangoObjectType):
    answers = DjangoFilterSetConnectionField(
        AnswerConnection, filterset_class=filters.AnswerFilterSet
    )
    meta = generic.GenericScalar()

    class Meta:
        model = models.Document
        exclude_fields = ("family",)
        interfaces = (graphene.Node,)


class TableAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.List(Document, required=True)

    def resolve_value(self, info, **args):
        return self.documents.order_by("-answerdocument__sort")

    class Meta:
        model = models.Answer
        exclude_fields = ("documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FormAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.Field(Document, required=True)

    def resolve_value(self, info, **args):
        return self.value_document

    class Meta:
        model = models.Answer
        exclude_fields = ("documents", "value_document", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class File(DjangoObjectType):
    name = graphene.String(required=True)
    upload_url = graphene.String()
    download_url = graphene.String()
    metadata = generic.GenericScalar()

    class Meta:
        model = models.File
        interfaces = (relay.Node,)


class FileAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.Field(File, required=True)

    def resolve_value(self, info, **args):
        return self.file

    class Meta:
        model = models.Answer
        exclude_fields = ("document", "documents", "value_document", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class SaveDocument(Mutation):
    class Meta:
        serializer_class = serializers.DocumentSerializer
        model_operations = ["create", "update"]


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


class SaveDocumentFormAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentFormAnswerSerializer
        return_field_type = Answer


class SaveDocumentFileAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentFileAnswerSerializer
        return_field_type = Answer


class RemoveAnswer(Mutation):
    class Meta:
        lookup_input_kwarg = "answer"
        serializer_class = serializers.RemoveAnswerSerializer


class Mutation(object):
    save_form = SaveForm().Field()
    copy_form = CopyForm().Field()
    add_form_question = AddFormQuestion().Field()
    remove_form_question = RemoveFormQuestion().Field()
    reorder_form_questions = ReorderFormQuestions().Field()

    save_option = SaveOption().Field()
    remove_option = RemoveOption().Field()
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
    save_file_question = SaveFileQuestion().Field()
    save_static_question = SaveStaticQuestion().Field()

    save_document = SaveDocument().Field()
    save_document_string_answer = SaveDocumentStringAnswer().Field()
    save_document_integer_answer = SaveDocumentIntegerAnswer().Field()
    save_document_float_answer = SaveDocumentFloatAnswer().Field()
    save_document_date_answer = SaveDocumentDateAnswer().Field()
    save_document_list_answer = SaveDocumentListAnswer().Field()
    save_document_table_answer = SaveDocumentTableAnswer().Field()
    save_document_form_answer = SaveDocumentFormAnswer().Field()
    save_document_file_answer = SaveDocumentFileAnswer().Field()
    remove_answer = RemoveAnswer().Field()


class Query(object):
    all_forms = DjangoFilterConnectionField(Form, filterset_class=filters.FormFilterSet)
    all_questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
    all_documents = DjangoFilterConnectionField(
        Document, filterset_class=filters.DocumentFilterSet
    )
