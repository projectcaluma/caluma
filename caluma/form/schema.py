import graphene
from graphene import relay
from graphene_django.rest_framework import serializer_converter

from . import filters, models, serializers
from ..filters import DjangoFilterConnectionField, DjangoFilterSetConnectionField
from ..mutation import Mutation, UserDefinedPrimaryKeyMixin
from ..relay import extract_global_id
from ..types import DjangoObjectType, Node


class QuestionJexl(graphene.String):
    """Question jexl represents a jexl expression returning boolean."""

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
    is_required = QuestionJexl(required=True)
    is_hidden = QuestionJexl(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = graphene.JSONString(required=True)
    forms = DjangoFilterConnectionField(
        "caluma.form.schema.Form", filterset_class=filters.FormFilterSet
    )

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return queryset.order_by("-formquestion__sort", "formquestion__id")

    @classmethod
    def resolve_type(cls, instance, info):
        QUESTION_OBJECT_TYPE = {
            models.Question.TYPE_TEXT: TextQuestion,
            models.Question.TYPE_FLOAT: FloatQuestion,
            models.Question.TYPE_RADIO: RadioQuestion,
            models.Question.TYPE_INTEGER: IntegerQuestion,
            models.Question.TYPE_CHECKBOX: CheckboxQuestion,
            models.Question.TYPE_TEXTAREA: TextareaQuestion,
        }

        return QUESTION_OBJECT_TYPE[instance.type]


class Option(DjangoObjectType):
    class Meta:
        model = models.Option
        interfaces = (relay.Node,)
        exclude_fields = ("questions",)

    @classmethod
    def get_queryset(cls, queryset, info):
        queryset = super().get_queryset(queryset, info)
        return queryset.order_by("-questionoption__sort", "questionoption__id")


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

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class TextareaQuestion(QuestionQuerysetMixin, DjangoObjectType):
    max_length = graphene.Int()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class RadioQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class CheckboxQuestion(QuestionQuerysetMixin, DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class IntegerQuestion(QuestionQuerysetMixin, DjangoObjectType):
    max_value = graphene.Int()
    min_value = graphene.Int()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class FloatQuestion(QuestionQuerysetMixin, DjangoObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class Form(DjangoObjectType):
    questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )

    class Meta:
        model = models.Form
        interfaces = (relay.Node,)
        exclude_fields = ("documents", "workflows")


class SaveForm(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveFormSerializer


class ArchiveForm(Mutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.ArchiveFormSerializer


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


class PublishForm(Mutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.PublishFormSerializer


class ArchiveQuestion(Mutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.ArchiveQuestionSerializer
        return_field_type = Question


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


class SaveRadioQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveRadioQuestionSerializer
        return_field_type = Question


class SaveCheckboxQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveCheckboxQuestionSerializer
        return_field_type = Question


class SaveIntegerQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveIntegerQuestionSerializer
        return_field_type = Question


class SaveFloatQuestion(SaveQuestion):
    class Meta:
        serializer_class = serializers.SaveFloatQuestionSerializer
        return_field_type = Question


class SaveOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        serializer_class = serializers.SaveOptionSerializer


class RemoveOption(UserDefinedPrimaryKeyMixin, Mutation):
    class Meta:
        lookup_input_kwarg = "option"
        serializer_class = serializers.RemoveOptionSerializer
        return_field_name = False


class Answer(Node, graphene.Interface):
    id = graphene.ID()
    created_at = graphene.DateTime(required=True)
    created_by_user = graphene.String()
    created_by_group = graphene.String()
    modified_at = graphene.DateTime(required=True)
    question = graphene.Field(Question, required=True)
    meta = graphene.JSONString(required=True)

    @classmethod
    def resolve_type(cls, instance, info):
        ANSWER_TYPE = {
            list: ListAnswer,
            str: StringAnswer,
            float: FloatAnswer,
            int: IntegerAnswer,
        }

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
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FloatAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.Float(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class StringAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.String(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class ListAnswer(AnswerQuerysetMixin, DjangoObjectType):
    value = graphene.List(graphene.String, required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class AnswerConnection(graphene.Connection):
    class Meta:
        node = Answer


class Document(DjangoObjectType):
    answers = DjangoFilterSetConnectionField(
        AnswerConnection, filterset_class=filters.AnswerFilterSet
    )

    class Meta:
        model = models.Document
        interfaces = (graphene.Node,)
        exclude_fields = ("cases",)
        filter_fields = ("form",)


class SaveDocument(Mutation):
    class Meta:
        serializer_class = serializers.DocumentSerializer


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


class Mutation(object):
    save_form = SaveForm().Field()
    archive_form = ArchiveForm().Field()
    publish_form = PublishForm().Field()
    add_form_question = AddFormQuestion().Field()
    remove_form_question = RemoveFormQuestion().Field()
    reorder_form_questions = ReorderFormQuestions().Field()

    save_option = SaveOption().Field()
    remove_option = RemoveOption().Field()

    save_text_question = SaveTextQuestion().Field()
    save_textarea_question = SaveTextareaQuestion().Field()
    save_radio_question = SaveRadioQuestion().Field()
    save_checkbox_question = SaveCheckboxQuestion().Field()
    save_float_question = SaveFloatQuestion().Field()
    save_integer_question = SaveIntegerQuestion().Field()
    archive_question = ArchiveQuestion().Field()

    save_document = SaveDocument().Field()
    save_document_string_answer = SaveDocumentStringAnswer().Field()
    save_document_integer_answer = SaveDocumentIntegerAnswer().Field()
    save_document_float_answer = SaveDocumentFloatAnswer().Field()
    save_document_list_answer = SaveDocumentListAnswer().Field()


class Query(object):
    all_forms = DjangoFilterConnectionField(Form, filterset_class=filters.FormFilterSet)
    all_questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
    all_documents = DjangoFilterConnectionField(
        Document, filterset_class=filters.DocumentFilterSet
    )
