import graphene
from django.shortcuts import get_object_or_404
from graphene import Node, relay
from graphene_django.fields import DjangoConnectionField
from graphene_django.types import DjangoObjectType
from graphql_relay import from_global_id

from . import models, serializers
from ..mutation import UserDefinedPrimaryKeyNodeSerializerMutation


class Form(DjangoObjectType):
    class Meta:
        model = models.Form
        interfaces = (Node,)


class SaveForm(UserDefinedPrimaryKeyNodeSerializerMutation):
    class Meta:
        serializer_class = serializers.FormSerializer


class DeleteForm(relay.ClientIDMutation):
    class Input:
        id = graphene.ID()

    form = graphene.Field(Form)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _, form_id = from_global_id(input["id"])
        form = get_object_or_404(models.Form, pk=form_id)
        form.delete()
        # pk is reset after delete
        form.slug = form_id
        return DeleteForm(form=form)


class Mutation(object):
    save_form = SaveForm().Field()
    delete_form = DeleteForm().Field()


class Query(object):
    all_forms = DjangoConnectionField(Form)
