import graphene
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene.types import ObjectType, generic
from graphene_django.rest_framework import serializer_converter

from ..caluma_core.filters import (
    CollectionFilterSetFactory,
    DjangoFilterConnectionField,
    DjangoFilterSetConnectionField,
)
from ..caluma_core.mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..caluma_core.relay import extract_global_id
from ..caluma_core.types import (
    ConnectionField,
    CountableConnectionBase,
    DjangoObjectType,
    Node,
)
from ..caluma_data_source.data_source_handlers import get_data_source_data
from ..caluma_data_source.schema import DataSourceDataConnection
from . import filters, models, serializers
from .format_validators import get_format_validators
from .validators import get_document_validity


def resolve_answer(answer):
    if answer.question.type == models.Question.TYPE_STATIC:
        raise Exception('Questions of type "static" should never have an answer!')
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

    Following transform can be used:
    * answer - access answer of document by question slug
    * mapby - map list by key. Helpful to work with table answers
      whereas an answer is a list of dicts.

    Following context is available:
    * form - access form of document

    Examples:
    * 'answer' == 'question-slug'|answer
    * 'answer' in 'list-question-slug'|answer
    * 'answer' in 'table-question-slug'|answer|mapby('column-question')
    * 'form-slug' == form

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
    is_required = QuestionJexl(
        required=True,
        description="Required expression is only evaluated when question is not hidden.",
    )
    is_hidden = QuestionJexl(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = generic.GenericScalar(required=True)
    forms = DjangoFilterConnectionField(
        "caluma.caluma_form.schema.Form", filterset_class=filters.FormFilterSet
    )
    source = graphene.Field("caluma.caluma_form.schema.Question")

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


class Option(FormDjangoObjectType):
    meta = generic.GenericScalar()

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
    regex = graphene.String(required=True)
    error_msg = graphene.String(required=True)


class FormatValidatorConnection(CountableConnectionBase):
    class Meta:
        node = FormatValidator


class TextQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    min_length = graphene.Int()
    max_length = graphene.Int()
    placeholder = graphene.String()
    format_validators = ConnectionField(FormatValidatorConnection)
    default_answer = graphene.Field("caluma.caluma_form.schema.StringAnswer")

    def resolve_format_validators(self, info):
        return get_format_validators(include=self.format_validators)

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
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TextareaQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    min_length = graphene.Int()
    max_length = graphene.Int()
    placeholder = graphene.String()
    format_validators = ConnectionField(FormatValidatorConnection)
    default_answer = graphene.Field("caluma.caluma_form.schema.StringAnswer")

    def resolve_format_validators(self, info):
        return get_format_validators(include=self.format_validators)

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
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DateQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
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
            "format_validators",
            "dynamicoption_set",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class ChoiceQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )
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
            "format_validators",
            "dynamicoption_set",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class MultipleChoiceQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )
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
            "format_validators",
            "dynamicoption_set",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicChoiceQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    options = ConnectionField(DataSourceDataConnection)
    data_source = graphene.String(required=True)

    def resolve_options(self, info, *args):
        return get_data_source_data(info, self.data_source)

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
            "format_validators",
            "dynamicoption_set",
            "default_answer",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicMultipleChoiceQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    options = ConnectionField(DataSourceDataConnection)
    data_source = graphene.String(required=True)

    def resolve_options(self, info, *args):
        return get_data_source_data(info, self.data_source)

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
            "format_validators",
            "dynamicoption_set",
            "default_answer",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class DynamicOption(DjangoObjectType):
    class Meta:
        model = models.DynamicOption
        interfaces = (relay.Node,)
        connection_class = CountableConnectionBase


class IntegerQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    max_value = graphene.Int()
    min_value = graphene.Int()
    placeholder = graphene.String()
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
            "format_validators",
            "dynamicoption_set",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FloatQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()
    placeholder = graphene.String()
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
            "format_validators",
            "dynamicoption_set",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class TableQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
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
            "format_validators",
            "dynamicoption_set",
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
            "static_content",
            "format_validators",
            "dynamicoption_set",
            "default_answer",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class FileQuestion(QuestionQuerysetMixin, FormDjangoObjectType):
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
            "format_validators",
            "dynamicoption_set",
            "default_answer",
        )
        use_connection = False
        interfaces = (Question, graphene.Node)


class Form(FormDjangoObjectType):
    questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
    meta = generic.GenericScalar()

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
        return resolve_answer(instance)


class AnswerQuerysetMixin(object):
    """Mixin to combine all different answer types into one queryset."""

    @classmethod
    def get_queryset(cls, queryset, info):
        return Answer.get_queryset(queryset, info)


class IntegerAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.Int()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FloatAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.Float()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class DateAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.types.datetime.Date()

    def resolve_value(self, info, **args):
        return self.date

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "file")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class StringAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.String()

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class ListAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.List(graphene.String)

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class AnswerConnection(CountableConnectionBase):
    class Meta:
        node = Answer


class Document(FormDjangoObjectType):
    answers = DjangoFilterSetConnectionField(
        AnswerConnection,
        filterset_class=CollectionFilterSetFactory(
            filters.AnswerFilterSet, orderset_class=filters.AnswerOrderSet
        ),
    )
    meta = generic.GenericScalar()

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
        exclude = ("documents", "file", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class File(FormDjangoObjectType):
    name = graphene.String(required=True)
    upload_url = graphene.String()
    download_url = graphene.String()
    metadata = generic.GenericScalar()
    answer = graphene.Field("caluma.caluma_form.schema.FileAnswer")

    class Meta:
        model = models.File
        interfaces = (relay.Node,)


class FileAnswer(AnswerQuerysetMixin, FormDjangoObjectType):
    value = graphene.Field(File, required=True)

    def resolve_value(self, info, **args):
        return self.file

    class Meta:
        model = models.Answer
        exclude = ("document", "documents", "date")
        use_connection = False
        interfaces = (Answer, graphene.Node)


class SaveDocument(Mutation):
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


class SaveDocumentFileAnswer(SaveDocumentAnswer):
    class Meta:
        serializer_class = serializers.SaveDocumentFileAnswerSerializer
        return_field_type = Answer


class RemoveAnswer(Mutation):
    class Meta:
        lookup_input_kwarg = "answer"
        serializer_class = serializers.RemoveAnswerSerializer
        return_field_type = Answer


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
    save_file_question = SaveFileQuestion().Field()
    save_static_question = SaveStaticQuestion().Field()

    copy_document = CopyDocument().Field()
    save_document = SaveDocument().Field()
    save_document_string_answer = SaveDocumentStringAnswer().Field()
    save_document_integer_answer = SaveDocumentIntegerAnswer().Field()
    save_document_float_answer = SaveDocumentFloatAnswer().Field()
    save_document_date_answer = SaveDocumentDateAnswer().Field()
    save_document_list_answer = SaveDocumentListAnswer().Field()
    save_document_table_answer = SaveDocumentTableAnswer().Field()
    save_document_file_answer = SaveDocumentFileAnswer().Field()
    remove_answer = RemoveAnswer().Field()
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


def validate_document(info, document_global_id):

    document_id = extract_global_id(document_global_id)

    document_qs = Document.get_queryset(models.Document.objects.all(), info)

    document = get_object_or_404(document_qs, pk=document_id)
    result = get_document_validity(document, info)

    errors = result.pop("errors")
    result = ValidationResult(
        **result, errors=[ValidationEntry(**err) for err in errors]
    )

    return [result]


class Query:
    all_forms = DjangoFilterConnectionField(
        Form,
        filterset_class=CollectionFilterSetFactory(
            filters.FormFilterSet, orderset_class=filters.FormOrderSet
        ),
    )
    all_questions = DjangoFilterSetConnectionField(
        QuestionConnection,
        filterset_class=CollectionFilterSetFactory(
            filters.QuestionFilterSet, orderset_class=filters.QuestionOrderSet
        ),
    )
    all_documents = DjangoFilterConnectionField(
        Document,
        filterset_class=CollectionFilterSetFactory(
            filters.DocumentFilterSet, filters.DocumentOrderSet
        ),
    )
    all_format_validators = ConnectionField(FormatValidatorConnection)
    all_used_dynamic_options = DjangoFilterConnectionField(
        DynamicOption,
        filterset_class=CollectionFilterSetFactory(filters.DynamicOptionFilterSet),
    )

    document_validity = ConnectionField(
        DocumentValidityConnection, id=graphene.ID(required=True)
    )

    def resolve_all_format_validators(self, info):
        return get_format_validators()

    def resolve_document_validity(self, info, id):
        return validate_document(info, id)


QUESTION_ANSWER_TYPES = {
    models.Question.TYPE_MULTIPLE_CHOICE: ListAnswer,
    models.Question.TYPE_INTEGER: IntegerAnswer,
    models.Question.TYPE_FLOAT: FloatAnswer,
    models.Question.TYPE_DATE: DateAnswer,
    models.Question.TYPE_CHOICE: StringAnswer,
    models.Question.TYPE_TEXTAREA: StringAnswer,
    models.Question.TYPE_TEXT: StringAnswer,
    models.Question.TYPE_TABLE: TableAnswer,
    models.Question.TYPE_FILE: FileAnswer,
    models.Question.TYPE_DYNAMIC_CHOICE: StringAnswer,
    models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE: ListAnswer,
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
    models.Question.TYPE_FILE: FileQuestion,
    models.Question.TYPE_STATIC: StaticQuestion,
}
