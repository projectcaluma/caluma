import graphene
from django.shortcuts import get_object_or_404
from graphene import relay
from graphene_django.converter import convert_django_field, convert_field_to_string
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.filter.filterset import GrapheneFilterSetMixin
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_relay import from_global_id
from localized_fields.fields import LocalizedField

from . import models, serializers
from ..filters import LocalizedFilter
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin

convert_django_field.register(LocalizedField, convert_field_to_string)
GrapheneFilterSetMixin.FILTER_DEFAULTS.update(
    {LocalizedField: {"filter_class": LocalizedFilter}}
)


class Form(DjangoObjectType):
    def resolve_questions(self, info):
        # TODO: potential cause for query explosions
        # see https://github.com/graphql-python/graphene-django/pull/220
        # and https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch
        return self.questions.order_by("-formquestion__sort", "formquestion__id")

    class Meta:
        model = models.Form
        filter_fields = ("slug", "name", "description", "is_published", "is_archived")
        interfaces = (relay.Node,)


class Question(DjangoObjectType):
    class Meta:
        model = models.Question
        filter_fields = (
            "slug",
            "label",
            "type",
            "is_required",
            "is_hidden",
            "is_archived",
        )
        interfaces = (relay.Node,)


class SaveForm(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.FormSerializer


class ArchiveForm(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["id"])
        form = get_object_or_404(models.Form, pk=form_id)
        form.is_archived = True
        form.save(update_fields=["is_archived"])
        return ArchiveForm(form=form)


class AddFormQuestion(relay.ClientIDMutation):
    """Add question at the end of form."""

    class Input:
        form_id = graphene.ID(required=True)
        question_id = graphene.ID(required=True)

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["form_id"])
        form = get_object_or_404(models.Form, pk=form_id)
        form.validate_editable()

        _, question_id = from_global_id(input["question_id"])
        question = get_object_or_404(models.Question, pk=question_id)

        models.FormQuestion.objects.create(form=form, question=question)
        return AddFormQuestion(form=form)


class RemoveFormQuestion(relay.ClientIDMutation):
    """Add question at the end of form."""

    class Input:
        form_id = graphene.ID(required=True)
        question_id = graphene.ID(required=True)

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["form_id"])
        form = get_object_or_404(models.Form, pk=form_id)
        form.validate_editable()

        _, question_id = from_global_id(input["question_id"])
        question = get_object_or_404(models.Question, pk=question_id)

        models.FormQuestion.objects.filter(form=form, question=question).delete()
        return RemoveFormQuestion(form=form)


class ReorderFormQuestions(relay.ClientIDMutation):
    class Input:
        form_id = graphene.ID(required=True)
        question_ids = graphene.List(graphene.ID, required=True)

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["form_id"])
        form = get_object_or_404(models.Form, pk=form_id)

        curr_questions = form.questions.values_list("slug", flat=True)
        inp_questions = [
            from_global_id(question_id)[1] for question_id in input["question_ids"]
        ]
        diff_questions = set(curr_questions).symmetric_difference(inp_questions)

        if diff_questions:
            raise GraphQLError(
                "Questions to reorder needs to match current form questions. Difference: "
                + ", ".join(diff_questions)
            )

        for sort, question in enumerate(reversed(inp_questions)):
            models.FormQuestion.objects.filter(form=form, question_id=question).update(
                sort=sort
            )

        return ReorderFormQuestions(form=form)


class PublishForm(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["id"])
        form = get_object_or_404(models.Form, pk=form_id)
        form.is_published = True
        form.save(update_fields=["is_published"])
        return PublishForm(form=form)


class ArchiveQuestion(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    question = graphene.Field(Question)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, question_id = from_global_id(input["id"])
        question = get_object_or_404(models.Question, pk=question_id)
        question.is_archived = True
        question.save(update_fields=["is_archived"])
        return ArchiveQuestion(question=question)


class SaveQuestion(UserDefinedPrimaryKeyMixin, SerializerMutation):
    class Meta:
        serializer_class = serializers.QuestionSerializer


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
    all_forms = DjangoFilterConnectionField(Form)
    all_questions = DjangoFilterConnectionField(Question)
