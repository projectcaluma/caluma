from graphene import List, String
from graphene_django import forms
from graphene_django.forms.converter import convert_form_field


class GlobalIDFormField(forms.GlobalIDFormField):
    """
    Global id form field which allows plain primary keys.

    Disable cleaning as input may be an actual relay global id
    or plain primary key.
    """

    def clean(self, value):
        return value


class GlobalIDMultipleChoiceField(forms.GlobalIDMultipleChoiceField):
    """
    Global id multiple choice field which allows plain primary keys.

    Disable cleaning as input may be an actual relay global id
    or plain primary key.
    """

    def valid_value(self, value):
        return True


class SlugMultipleChoiceField(GlobalIDMultipleChoiceField):
    """
    Slug multiple choice field which allows listing multiple slugs.

    Disable cleaning as we don't know which slugs may be valid down
    the line
    """

    def valid_value(self, value):  # pragma: no cover
        return True


@convert_form_field.register(SlugMultipleChoiceField)
def slug_to_list(field):
    return List(String, required=field.required)
