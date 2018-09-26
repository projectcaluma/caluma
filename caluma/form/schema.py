import graphene
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene.relay.mutation import ClientIDMutation
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import filters, models, serializers
from ..filters import DjangoFilterSetConnectionField
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin
from ..relay import extract_global_id


class Question(graphene.Interface):
    id = graphene.ID(required=True)
    created = graphene.DateTime(required=True)
    modified = graphene.DateTime(required=True)
    slug = graphene.String(required=True)
    label = graphene.String(required=True)
    is_required = graphene.String(required=True)
    is_hidden = graphene.String(required=True)
    is_archived = graphene.Boolean(required=True)
    meta = graphene.JSONString()
    forms = DjangoFilterConnectionField(
        "caluma.form.schema.Form", filterset_class=filters.FormFilterSet
    )

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
        only_fields = ("created", "modified", "label", "slug", "meta")


class QuestionConnection(graphene.Connection):
    class Meta:
        node = Question


class TextQuestion(graphene.ObjectType):
    max_length = graphene.Int(required=True)

    class Meta:
        interfaces = (Question, graphene.Node)


class TextareaQuestion(graphene.ObjectType):
    max_length = graphene.Int(required=True)

    class Meta:
        interfaces = (Question, graphene.Node)


class RadioQuestion(graphene.ObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        interfaces = (Question, graphene.Node)


class CheckboxQuestion(graphene.ObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    class Meta:
        interfaces = (Question, graphene.Node)


class IntegerQuestion(graphene.ObjectType):
    max_value = graphene.Int(required=True)
    min_value = graphene.Int(required=True)

    class Meta:
        interfaces = (Question, graphene.Node)


class FloatQuestion(graphene.ObjectType):
    min_value = graphene.Float(required=True)
    max_value = graphene.Float(required=True)

    class Meta:
        interfaces = (Question, graphene.Node)


class Form(DjangoObjectType):
    questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )

    def resolve_questions(self, info, **kwargs):
        # TODO: potential cause for query explosions.
        # https://github.com/graphql-python/graphene-django/pull/220
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch
        return self.questions.order_by("-formquestion__sort", "formquestion__id")

    class Meta:
        model = models.Form
        interfaces = (relay.Node,)
        only_fields = (
            "created",
            "modified",
            "slug",
            "name",
            "description",
            "meta",
            "is_published",
            "is_archived",
        )


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


class SaveQuestionOption(ClientIDMutation):
    question = graphene.Field(Question)

    class Input:
        question = graphene.ID(required=True)
        slug = graphene.String(required=True)
        label = graphene.String(required=True)
        meta = graphene.JSONString(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        question_id = extract_global_id(input["question"])
        option = models.Option.objects.filter(question=question_id).first()

        serializer = serializers.OptionSerializer(
            data=input, instance=option, context={"request": info.context}
        )
        serializer.is_valid(raise_exception=True)
        option = serializer.save()

        return cls(question=option.question)


class RemoveQuestionOption(ClientIDMutation):
    question = graphene.Field(Question)

    class Input:
        question = graphene.ID()
        option = graphene.ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        question_id = extract_global_id(input["question"])
        question = get_object_or_404(models.Question.objects, pk=question_id)
        option_id = extract_global_id(input["option"])

        models.Option.objects.filter(question=question_id, pk=option_id).delete()

        return cls(question=question)


class Mutation(object):
    save_form = SaveForm().Field()
    archive_form = ArchiveForm().Field()
    publish_form = PublishForm().Field()
    add_form_question = AddFormQuestion().Field()
    remove_form_question = RemoveFormQuestion().Field()
    reorder_form_questions = ReorderFormQuestions().Field()

    save_text_question = SaveTextQuestion().Field()
    save_textarea_question = SaveTextareaQuestion().Field()
    save_radio_question = SaveRadioQuestion().Field()
    save_checkbox_question = SaveCheckboxQuestion().Field()
    save_float_question = SaveFloatQuestion().Field()
    save_integer_question = SaveIntegerQuestion().Field()
    save_question_option = SaveQuestionOption().Field()
    remove_question_option = RemoveQuestionOption().Field()
    archive_question = ArchiveQuestion().Field()


class Query(object):
    all_forms = DjangoFilterConnectionField(Form, filterset_class=filters.FormFilterSet)
    all_questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
