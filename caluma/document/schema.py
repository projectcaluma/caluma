import graphene
from graphene.relay.mutation import ClientIDMutation
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import filters, models, serializers
from ..form.schema import Question
from ..mutation import SerializerMutation
from ..relay import extract_global_id


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


class Document(DjangoObjectType):
    answers = graphene.ConnectionField(AnswerConnection)

    def resolve_answers(self, info, **kwargs):
        return self.answers.all()

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
    save_document = SaveDocument().Field()
    save_document_string_answer = SaveDocumentStringAnswer().Field()
    save_document_integer_answer = SaveDocumentIntegerAnswer().Field()
    save_document_float_answer = SaveDocumentFloatAnswer().Field()
    save_document_list_answer = SaveDocumentListAnswer().Field()


class Query(object):
    all_documents = DjangoFilterConnectionField(
        Document, filterset_class=filters.DocumentFilterSet
    )
