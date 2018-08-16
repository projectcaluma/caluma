from graphene import Node
from graphene_django.fields import DjangoConnectionField
from graphene_django.types import DjangoObjectType

from . import models, serializers
from ..mutation import UserDefinedPrimaryKeyNodeSerializerMutation


class Form(DjangoObjectType):
    class Meta:
        model = models.Form
        interfaces = (Node,)


class SaveForm(UserDefinedPrimaryKeyNodeSerializerMutation):
    class Meta:
        serializer_class = serializers.FormSerializer


class Mutation(object):
    save_form = SaveForm().Field()


class Query(object):
    all_forms = DjangoConnectionField(Form)
