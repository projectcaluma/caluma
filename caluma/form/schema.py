from graphene import Node
from graphene_django.fields import DjangoConnectionField
from graphene_django.types import DjangoObjectType

from . import models


class Form(DjangoObjectType):
    class Meta:
        model = models.Form
        interfaces = (Node,)


class Query(object):
    all_forms = DjangoConnectionField(Form)
