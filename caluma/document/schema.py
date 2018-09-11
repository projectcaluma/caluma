import graphene
from graphene.relay.mutation import ClientIDMutation
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay import from_global_id

from . import models, serializers
from ..form.schema import Question
from ..mutation import SerializerMutation


class Answer(graphene.Interface):
    id = graphene.ID()
    question = graphene.Field(Question, required=True)
    meta = graphene.JSONString()


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


def create_answer_node(answer):
    ANSWER_TYPE = {
        list: ListAnswer,
        str: StringAnswer,
        float: FloatAnswer,
        int: IntegerAnswer,
    }

    answer_type = ANSWER_TYPE[type(answer.value)]
    return answer_type(
        id=answer.id, question=answer.question, meta=answer.meta, value=answer.value
    )


class Document(DjangoObjectType):
    answers = graphene.ConnectionField(AnswerConnection)

    def resolve_answers(self, info):
        # TODO: filter by question
        return [create_answer_node(answer) for answer in self.answers.all()]

    class Meta:
        model = models.Document
        interfaces = (graphene.Node,)
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
        _, question_id = from_global_id(input["question"])
        _, document_id = from_global_id(input["document"])
        answer = models.Answer.objects.filter(
            question=question_id, document=document_id
        ).first()

        serializer = serializers.AnswerSerializer(
            data=input, instance=answer, context={"request": info.context}
        )
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        return cls(answer=create_answer_node(answer))


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
    all_documents = DjangoFilterConnectionField(Document)
