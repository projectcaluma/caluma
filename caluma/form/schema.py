import graphene
from graphene import relay
from graphene.relay.mutation import ClientIDMutation
from graphene_django.rest_framework import serializer_converter

from . import filters, models, serializers
from ..filters import DjangoFilterConnectionField, DjangoFilterSetConnectionField
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin
from ..relay import extract_global_id
from ..types import DjangoObjectType


class QuestionJexl(graphene.String):
    """Question jexl represents a jexl expression returning boolean."""

    pass


serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.QuestionJexlField, lambda field: QuestionJexl
)


class Question(graphene.Interface):
    id = graphene.ID(required=True)
    created = graphene.DateTime(required=True)
    modified = graphene.DateTime(required=True)
    slug = graphene.String(required=True)
    label = graphene.String(required=True)
    is_required = QuestionJexl(required=True)
    is_hidden = QuestionJexl(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = graphene.JSONString()
    forms = DjangoFilterConnectionField(
        "caluma.form.schema.Form", filterset_class=filters.FormFilterSet
    )

    @classmethod
    def get_queryset(cls, queryset, info):
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
        return queryset.order_by("-questionoption__sort", "questionoption__id")


class QuestionConnection(graphene.Connection):
    class Meta:
        node = Question


class TextQuestion(DjangoObjectType):
    max_length = graphene.Int()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class TextareaQuestion(DjangoObjectType):
    max_length = graphene.Int()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class RadioQuestion(DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class CheckboxQuestion(DjangoObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class IntegerQuestion(DjangoObjectType):
    max_value = graphene.Int()
    min_value = graphene.Int()

    class Meta:
        model = models.Question
        exclude_fields = ("type", "configuration", "options", "answers")
        use_connection = False
        interfaces = (Question, graphene.Node)


class FloatQuestion(DjangoObjectType):
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


class SaveForm(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveFormSerializer


class ArchiveForm(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.ArchiveFormSerializer


class AddFormQuestion(SerializerMutation):
    """Add question at the end of form."""

    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.AddFormQuestionSerializer


class RemoveFormQuestion(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.RemoveFormQuestionSerializer


class ReorderFormQuestions(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "form"
        serializer_class = serializers.ReorderFormQuestionsSerializer


class PublishForm(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.PublishFormSerializer


class ArchiveQuestion(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.ArchiveQuestionSerializer
        return_field_type = Question


class SaveTextQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveTextQuestionSerializer
        return_field_type = Question


class SaveTextareaQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveTextareaQuestionSerializer
        return_field_type = Question


class SaveRadioQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveRadioQuestionSerializer
        return_field_type = Question


class SaveCheckboxQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveCheckboxQuestionSerializer
        return_field_type = Question


class SaveIntegerQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveIntegerQuestionSerializer
        return_field_type = Question


class SaveFloatQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveFloatQuestionSerializer
        return_field_type = Question


class SaveOption(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveOptionSerializer


class RemoveOption(ClientIDMutation):
    class Input:
        option = graphene.ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        option_id = extract_global_id(input["option"])
        models.Option.objects.filter(pk=option_id).delete()
        return cls()


class Answer(graphene.Interface):
    id = graphene.ID()
    created = graphene.DateTime(required=True)
    modified = graphene.DateTime(required=True)
    question = graphene.Field(Question, required=True)
    meta = graphene.JSONString()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    @classmethod
    def resolve_type(cls, instance, info):
        ANSWER_TYPE = {
            list: ListAnswer,
            str: StringAnswer,
            float: FloatAnswer,
            int: IntegerAnswer,
        }

        return ANSWER_TYPE[type(instance.value)]


class IntegerAnswer(DjangoObjectType):
    value = graphene.Int(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class FloatAnswer(DjangoObjectType):
    value = graphene.Float(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class StringAnswer(DjangoObjectType):
    value = graphene.String(required=True)

    class Meta:
        model = models.Answer
        exclude_fields = ("document",)
        use_connection = False
        interfaces = (Answer, graphene.Node)


class ListAnswer(DjangoObjectType):
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
        only_fields = ("created", "modified", "form", "meta", "answers")
        filter_fields = ("form",)


class SaveDocument(SerializerMutation):
    class Meta:
        serializer_class = serializers.DocumentSerializer


class SaveDocumentAnswer(ClientIDMutation):
    # TODO: could be simplified once following issue is addressed:
    # https://github.com/graphql-python/graphene-django/issues/121
    class Meta:
        abstract = True

    answer = graphene.Field(Answer)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        question_id = extract_global_id(input["question"])
        document_id = extract_global_id(input["document"])
        answer = models.Answer.objects.filter(
            question=question_id, document=document_id
        ).first()

        serializer = serializers.AnswerSerializer(
            data=input, instance=answer, context={"request": info.context}
        )
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        return cls(answer=answer)


class SaveDocumentStringAnswer(SaveDocumentAnswer):
    class Input:
        question = graphene.ID(required=True)
        document = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.String(required=True)


class SaveDocumentListAnswer(SaveDocumentAnswer):
    class Input:
        question = graphene.ID(required=True)
        document = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.List(graphene.String, required=True)


class SaveDocumentIntegerAnswer(SaveDocumentAnswer):
    class Input:
        question = graphene.ID(required=True)
        document = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.Int(required=True)


class SaveDocumentFloatAnswer(SaveDocumentAnswer):
    class Input:
        question = graphene.ID(required=True)
        document = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.Float(required=True)


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
