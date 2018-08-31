import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import models
from ..form.schema import Question


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


ANSWER_TYPE = {
    list: ListAnswer,
    str: StringAnswer,
    float: FloatAnswer,
    int: IntegerAnswer,
}


class Document(DjangoObjectType):
    answers = graphene.ConnectionField(AnswerConnection)

    def resolve_answers(self, info):
        # TODO: filter by question
        answers = []
        for answer in self.answers.all():
            answer_type = ANSWER_TYPE[type(answer.value)]
            answers.append(
                answer_type(
                    id=answer.id,
                    question=answer.question,
                    meta=answer.meta,
                    value=answer.value,
                )
            )

        return answers

    class Meta:
        model = models.Document
        interfaces = (graphene.Node,)
        filter_fields = ("form",)


class Query(object):
    all_documents = DjangoFilterConnectionField(Document)
