import graphene
from django.http import Http404
from graphene import relay
from graphene.types import ObjectType, generic

from ..core.relay import extract_global_id
from ..core.types import ConnectionField, CountableConnectionBase
from . import models
from .schema import (
    Answer,
    DateAnswer,
    FileAnswer,
    FloatAnswer,
    FormDjangoObjectType,
    IntegerAnswer,
    ListAnswer,
    StringAnswer,
    TableAnswer,
    resolve_answer,
)
from .storage_clients import client


def historical_qs_as_of(queryset, date, pk_attr):
    """Get history revision as of `date` for queryset.

    :param queryset: history qs
    :param date: aware datetime()
    :param pk_attr: str (pk field name)
    """
    # TODO: This could be optimised with some sql magic in order to return a queryset.
    # This could become unnecessary as soon as
    # https://github.com/treyhunner/django-simple-history/issues/397 is resolved.
    queryset = queryset.filter(history_date__lte=date)
    for original_pk in set(queryset.values_list(pk_attr, flat=True)):
        changes = queryset.filter(**{pk_attr: original_pk})
        last_change = changes.latest("history_date")
        if changes.filter(
            history_date=last_change.history_date, history_type="-"
        ).exists():
            continue
        yield last_change


def resolve_historical_answer(answer):
    answer_type = resolve_answer(answer)
    return eval(f"Historical{answer_type.__name__}")


class HistoricalAnswer(Answer):
    history_date = graphene.types.datetime.DateTime(required=True)
    history_user_id = graphene.String()
    history_type = graphene.String()

    @classmethod
    def resolve_type(cls, instance, info):
        return resolve_historical_answer(instance)


class HistoricalAnswerConnection(CountableConnectionBase):
    class Meta:
        node = HistoricalAnswer


class HistoricalIntegerAnswer(IntegerAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalFloatAnswer(FloatAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalDateAnswer(DateAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "file")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalStringAnswer(StringAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalListAnswer(ListAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalFile(ObjectType):
    name = graphene.String(required=True)
    download_url = graphene.String()
    metadata = generic.GenericScalar()
    historical_answer = graphene.Field(
        "caluma.form.historical_schema.HistoricalFileAnswer"
    )
    history_date = graphene.types.datetime.DateTime(required=True)
    history_user_id = graphene.String()
    history_type = graphene.String()

    @classmethod
    def resolve_download_url(cls, instance, info):
        # if the file is part of the newest revision, the downloadUri has to be for the
        # actual file object_name.
        if instance == instance.instance.history.first():
            return instance.instance.download_url
        return client.download_url(f"{instance.pk}_{instance.name}")

    class Meta:
        model = models.File.history.model
        interfaces = (relay.Node,)


class HistoricalFileAnswer(FileAnswer):
    value = graphene.Field(
        HistoricalFile,
        required=True,
        as_of=graphene.types.datetime.DateTime(required=True),
    )

    def resolve_value(self, info, as_of, **args):
        # we need to use the HistoricalFile of the correct revision
        return models.File.history.filter(
            id=self.file_id, history_date__lte=as_of
        ).first()

    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "documents", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalDocument(FormDjangoObjectType):
    historical_answers = ConnectionField(
        HistoricalAnswerConnection,
        as_of=graphene.types.datetime.DateTime(required=True),
    )
    history_date = graphene.types.datetime.DateTime(required=True)
    history_user_id = graphene.String()
    history_type = graphene.String()
    meta = generic.GenericScalar()

    def resolve_historical_answers(self, info, as_of, *args):
        answers = [
            a
            for a in historical_qs_as_of(
                models.Answer.history.filter(document_id=self.id), as_of, "id"
            )
        ]
        return answers

    class Meta:
        model = models.Document.history.model
        exclude = ("family", "history_id", "history_change_reason")
        interfaces = (graphene.Node,)
        connection_class = CountableConnectionBase


class HistoricalTableAnswer(TableAnswer):
    value = graphene.List(
        HistoricalDocument,
        required=True,
        as_of=graphene.types.datetime.DateTime(required=True),
    )

    def resolve_value(self, info, as_of, *args):
        answerdocuments = [
            ad
            for ad in historical_qs_as_of(
                models.AnswerDocument.history.filter(answer_id=self.id), as_of, "id"
            )
        ]

        answerdocuments.sort(key=lambda x: x.sort)

        documents = [
            models.Document.history.filter(id=ad.document_id).filter(
                history_date__lte=as_of
            )[0]
            for ad in answerdocuments
        ]

        return documents

    class Meta:
        model = models.Answer.history.model
        exclude = ("documents", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


def document_as_of(info, document_global_id, timestamp):
    document_id = extract_global_id(document_global_id)
    document_qs = HistoricalDocument.get_queryset(models.Document.history.all(), info)
    document = document_qs.filter(id=document_id, history_date__lte=timestamp).first()
    if not document:
        raise Http404("No HistoricalDocument matches the given query.")
    return document


class Query:
    document_as_of = graphene.Field(
        HistoricalDocument,
        id=graphene.ID(required=True),
        as_of=graphene.types.datetime.DateTime(required=True),
    )

    def resolve_document_as_of(self, info, id, as_of):
        return document_as_of(info, id, as_of)
