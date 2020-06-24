import graphene
from django.http import Http404
from graphene import relay
from graphene.types import ObjectType, generic

from ..caluma_core.relay import extract_global_id
from ..caluma_core.types import ConnectionField, CountableConnectionBase
from . import models
from .schema import (
    QUESTION_ANSWER_TYPES,
    Answer,
    DateAnswer,
    FileAnswer,
    FloatAnswer,
    FormDjangoObjectType,
    IntegerAnswer,
    ListAnswer,
    StringAnswer,
    TableAnswer,
)
from .storage_clients import client


def historical_qs_as_of(queryset, date, pk_attr):
    """Get history revision as of `date` for queryset.

    :param queryset: history Queryset()
    :param date: aware datetime()
    :param pk_attr: str (pk field name)
    :return: Queryset()
    """
    # This could become unnecessary as soon as
    # https://github.com/treyhunner/django-simple-history/issues/397 is resolved.
    return (
        queryset.filter(history_date__lte=date)
        .order_by(pk_attr, "-history_date")
        .distinct(pk_attr)
    )


class HistoricalAnswer(Answer):
    history_date = graphene.types.datetime.DateTime(required=True)
    history_user_id = graphene.String()
    history_type = graphene.String()

    @classmethod
    def resolve_type(cls, instance, info):
        answer_type = QUESTION_ANSWER_TYPES[instance.history_question_type]
        return f"Historical{answer_type.__name__}"


class HistoricalAnswerConnection(CountableConnectionBase):
    class Meta:
        node = HistoricalAnswer


class HistoricalIntegerAnswer(IntegerAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalFloatAnswer(FloatAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalDateAnswer(DateAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "file")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalStringAnswer(StringAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalListAnswer(ListAnswer):
    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "file", "date")
        use_connection = False
        interfaces = (HistoricalAnswer, graphene.Node)


class HistoricalFile(ObjectType):
    name = graphene.String(required=True)
    download_url = graphene.String()
    metadata = generic.GenericScalar()
    historical_answer = graphene.Field(
        "caluma.caluma_form.historical_schema.HistoricalFileAnswer"
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
        required=False,
        as_of=graphene.types.datetime.DateTime(required=True),
    )

    def resolve_value(self, info, as_of, **args):
        # we need to use the HistoricalFile of the correct revision
        return models.File.history.filter(
            id=self.file_id, history_date__lte=as_of
        ).first()

    class Meta:
        model = models.Answer.history.model
        exclude = ("document", "date")
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
    document_id = graphene.UUID()

    def resolve_document_id(self, info, *args):
        return self.id

    def resolve_historical_answers(self, info, as_of, *args):
        return historical_qs_as_of(
            models.Answer.history.filter(document_id=self.id), as_of, "id"
        )

    class Meta:
        model = models.Document.history.model
        exclude = ("family", "history_id", "history_change_reason")
        interfaces = (graphene.Node,)
        connection_class = CountableConnectionBase


class HistoricalTableAnswer(TableAnswer):
    value = graphene.List(
        HistoricalDocument,
        required=False,
        as_of=graphene.types.datetime.DateTime(required=True),
    )

    def resolve_value(self, info, as_of, *args):
        answerdocuments_unordered = historical_qs_as_of(
            models.AnswerDocument.history.filter(answer_id=self.id), as_of, "id"
        )

        # ordering has to happen in a separate query because of the use of `distinct()`
        answerdocuments = models.AnswerDocument.history.filter(
            pk__in=answerdocuments_unordered
        ).order_by("sort")

        documents = [
            models.Document.history.filter(
                id=ad.document_id, history_date__lte=as_of
            ).latest("history_date")
            for ad in answerdocuments
        ]

        # Since python 3.6, `list(dict.fromkeys(somelist))` is the most performant way
        # to remove duplicates from a list, while retaining it's order.
        # In python 3.6 this is an implementation detail. From python 3.7 onwards it is
        # a language feature.
        # Luckily django model instances are hashable, so we're able to make use of
        # this.
        return list(dict.fromkeys(documents))

    class Meta:
        model = models.Answer.history.model
        exclude = ("file", "date")
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
