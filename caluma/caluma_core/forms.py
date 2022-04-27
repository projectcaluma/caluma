from graphene_django import forms


class GlobalIDFormField(forms.GlobalIDFormField):
    """
    Global id form field which allows plain primary keys.

    Disable cleaning as input may be an actual relay global id
    or plain primary key.
    """

    def clean(self, value):  # pragma: no cover
        return value


class GlobalIDMultipleChoiceField(forms.GlobalIDMultipleChoiceField):
    """
    Global id multiple choice field which allows plain primary keys.

    Disable cleaning as input may be an actual relay global id
    or plain primary key.
    """

    def valid_value(self, value):  # pragma: no cover
        return True
