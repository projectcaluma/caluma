import graphene
from graphene import relay
from graphene.relay.mutation import ClientIDMutation
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework import serializer_converter
from graphene_django.types import DjangoObjectType

from . import filters, models, serializers
from ..filters import DjangoFilterSetConnectionField
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin
from ..relay import extract_global_id


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
    form_specifications = DjangoFilterConnectionField(
        "caluma.form.schema.FormSpecification",
        filterset_class=filters.FormSpecificationFilterSet,
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
    max_length = graphene.Int()

    class Meta:
        interfaces = (Question, graphene.Node)


class TextareaQuestion(graphene.ObjectType):
    max_length = graphene.Int()

    class Meta:
        interfaces = (Question, graphene.Node)


class RadioQuestion(graphene.ObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    def resolve_options(self, info, **kwargs):
        return self.options.order_by("-questionoption__sort", "questionoption__id")

    class Meta:
        interfaces = (Question, graphene.Node)


class CheckboxQuestion(graphene.ObjectType):
    options = DjangoFilterConnectionField(
        Option, filterset_class=filters.OptionFilterSet
    )

    def resolve_options(self, info, **kwargs):
        return self.options.order_by("-questionoption__sort", "questionoption__id")

    class Meta:
        interfaces = (Question, graphene.Node)


class IntegerQuestion(graphene.ObjectType):
    max_value = graphene.Int()
    min_value = graphene.Int()

    class Meta:
        interfaces = (Question, graphene.Node)


class FloatQuestion(graphene.ObjectType):
    min_value = graphene.Float()
    max_value = graphene.Float()

    class Meta:
        interfaces = (Question, graphene.Node)


class FormSpecification(DjangoObjectType):
    questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )

    def resolve_questions(self, info, **kwargs):
        # TODO: potential cause for query explosions.
        # https://github.com/graphql-python/graphene-django/pull/220
        # https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch
        return self.questions.order_by(
            "-formspecificationquestion__sort", "formspecificationquestion__id"
        )

    class Meta:
        model = models.FormSpecification
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


class SaveFormSpecification(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveFormSpecificationSerializer


class ArchiveFormSpecification(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.ArchiveFormSpecificationSerializer


class AddFormSpecificationQuestion(SerializerMutation):
    """Add question at the end of form specification."""

    class Meta:
        lookup_input_kwarg = "form_specification"
        serializer_class = serializers.AddFormSpecificationQuestionSerializer


class RemoveFormSpecificationQuestion(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "form_specification"
        serializer_class = serializers.RemoveFormSpecificationQuestionSerializer


class ReorderFormSpecificationQuestions(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "form_specification"
        serializer_class = serializers.ReorderFormSpecificationQuestionsSerializer


class PublishFormSpecification(SerializerMutation):
    class Meta:
        lookup_input_kwarg = "id"
        serializer_class = serializers.PublishFormSpecificationSerializer


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
    def resolve_type(cls, instance, info):
        ANSWER_TYPE = {
            list: ListAnswer,
            str: StringAnswer,
            float: FloatAnswer,
            int: IntegerAnswer,
        }

        return ANSWER_TYPE[type(instance.value)]


class IntegerAnswer(graphene.ObjectType):
    value = graphene.Int(required=True)

    class Meta:
        interfaces = (Answer, graphene.Node)


class FloatAnswer(graphene.ObjectType):
    value = graphene.Float(required=True)

    class Meta:
        interfaces = (Answer, graphene.Node)


class StringAnswer(graphene.ObjectType):
    value = graphene.String(required=True)

    class Meta:
        interfaces = (Answer, graphene.Node)


class ListAnswer(graphene.ObjectType):
    value = graphene.List(graphene.String, required=True)

    class Meta:
        interfaces = (Answer, graphene.Node)


class AnswerConnection(graphene.Connection):
    class Meta:
        node = Answer


class Form(DjangoObjectType):
    answers = graphene.ConnectionField(AnswerConnection)

    def resolve_answers(self, info, **kwargs):
        return self.answers.all()

    class Meta:
        model = models.Form
        interfaces = (graphene.Node,)
        only_fields = ("created", "modified", "form_specification", "meta", "answers")
        filter_fields = ("form_specification",)


class SaveForm(SerializerMutation):
    class Meta:
        serializer_class = serializers.FormSerializer


class SaveFormAnswer(ClientIDMutation):
    class Meta:
        abstract = True

    answer = graphene.Field(Answer)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        question_id = extract_global_id(input["question"])
        form_id = extract_global_id(input["form"])
        answer = models.Answer.objects.filter(
            question=question_id, form=form_id
        ).first()

        serializer = serializers.AnswerSerializer(
            data=input, instance=answer, context={"request": info.context}
        )
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        return cls(answer=answer)


class SaveFormStringAnswer(SaveFormAnswer):
    class Input:
        question = graphene.ID(required=True)
        form = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.String(required=True)


class SaveFormListAnswer(SaveFormAnswer):
    class Input:
        question = graphene.ID(required=True)
        form = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.List(graphene.String, required=True)


class SaveFormIntegerAnswer(SaveFormAnswer):
    class Input:
        question = graphene.ID(required=True)
        form = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.Int(required=True)


class SaveFormFloatAnswer(SaveFormAnswer):
    class Input:
        question = graphene.ID(required=True)
        form = graphene.ID(required=True)
        meta = graphene.JSONString(required=True)
        value = graphene.Float(required=True)


class Mutation(object):
    save_form_specification = SaveFormSpecification().Field()
    archive_form_specification = ArchiveFormSpecification().Field()
    publish_form_specification = PublishFormSpecification().Field()
    add_form_specification_question = AddFormSpecificationQuestion().Field()
    remove_form_specification_question = RemoveFormSpecificationQuestion().Field()
    reorder_form_specification_questions = ReorderFormSpecificationQuestions().Field()

    save_option = SaveOption().Field()
    remove_option = RemoveOption().Field()

    save_text_question = SaveTextQuestion().Field()
    save_textarea_question = SaveTextareaQuestion().Field()
    save_radio_question = SaveRadioQuestion().Field()
    save_checkbox_question = SaveCheckboxQuestion().Field()
    save_float_question = SaveFloatQuestion().Field()
    save_integer_question = SaveIntegerQuestion().Field()
    archive_question = ArchiveQuestion().Field()

    save_form = SaveForm().Field()
    save_form_string_answer = SaveFormStringAnswer().Field()
    save_form_integer_answer = SaveFormIntegerAnswer().Field()
    save_form_float_answer = SaveFormFloatAnswer().Field()
    save_form_list_answer = SaveFormListAnswer().Field()


class Query(object):
    all_form_specifications = DjangoFilterConnectionField(
        FormSpecification, filterset_class=filters.FormSpecificationFilterSet
    )
    all_questions = DjangoFilterSetConnectionField(
        QuestionConnection, filterset_class=filters.QuestionFilterSet
    )
    all_forms = DjangoFilterConnectionField(Form, filterset_class=filters.FormFilterSet)
