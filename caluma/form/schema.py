import graphene
from django.shortcuts import get_object_or_404
from graphene import Node, relay
from graphene_django.fields import DjangoConnectionField
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_relay import from_global_id

from . import models, serializers
from ..mutation import SerializerMutation, UserDefinedPrimaryKeyMixin


class Form(DjangoObjectType):
    def resolve_questions(self, info):
        # TODO: potential cause for query explosions
        # see https://github.com/graphql-python/graphene-django/pull/220
        # and https://docs.djangoproject.com/en/2.1/ref/models/querysets/#django.db.models.Prefetch
        return self.questions.order_by("-formquestion__sort", "formquestion__id")

    class Meta:
        model = models.Form
        interfaces = (Node,)


class Question(DjangoObjectType):
    class Meta:
        model = models.Question
        interfaces = (Node,)


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

        if form.is_archived or form.is_published:
            raise GraphQLError(
                "Form %s may not be edited as it is archived or published" % form_id
            )

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

        if form.is_archived or form.is_published:
            raise GraphQLError(
                "Form %s may not be edited as it is archived or published" % form_id
            )

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
    all_forms = DjangoConnectionField(Form)
    all_questions = DjangoConnectionField(Question)
