from graphene import relay
from graphene_django.converter import convert_django_field, convert_field_to_string
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from localized_fields.fields import LocalizedField

from . import filters, models, serializers
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin

convert_django_field.register(LocalizedField, convert_field_to_string)


class Question(DjangoObjectType):
    forms = DjangoFilterConnectionField(
        "caluma.form.schema.Form", filterset_class=filters.FormFilterSet
    )

    class Meta:
        model = models.Question
        interfaces = (relay.Node,)
        only_fields = (
            "created",
            "modified",
            "slug",
            "label",
            "type",
            "is_required",
            "is_hidden",
            "is_archived",
            "meta",
            "configuration",
            "forms",
            "id",
        )


class Form(DjangoObjectType):
    questions = DjangoFilterConnectionField(
        Question, filterset_class=filters.QuestionFilterSet
    )

    def resolve_questions(self, info, **kwargs):
        # TODO: potential cause for query explosions
        # see https://github.com/graphql-python/graphene-django/pull/220
        # and https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch
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
            "questions",
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


class SaveQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.SaveQuestionSerializer


class Mutation(object):
    save_form = SaveForm().Field()
    archive_form = ArchiveForm().Field()
    publish_form = PublishForm().Field()
    add_form_question = AddFormQuestion().Field()
    remove_form_question = RemoveFormQuestion().Field()
    reorder_form_questions = ReorderFormQuestions().Field()

    save_question = SaveQuestion().Field()
    archive_question = ArchiveQuestion().Field()


class Query(object):
    all_forms = DjangoFilterConnectionField(Form, filterset_class=filters.FormFilterSet)
    all_questions = DjangoFilterConnectionField(
        Question, filterset_class=filters.QuestionFilterSet
    )
