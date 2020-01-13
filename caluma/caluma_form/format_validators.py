import re
from collections import namedtuple

from django.conf import settings
from django.utils.module_loading import import_string
from localized_fields.value import LocalizedValue
from rest_framework.exceptions import ValidationError


class BaseFormatValidator:
    r"""Basic format validator class to be extended by any format validator implementation.

    A custom format validator class could look like this:
    ```
    >>> from caluma.caluma_form.format_validators import BaseFormatValidator
    ...
    ...
    ... class CustomFormatValidator(BaseFormatValidator):
    ...     slug = "email"
    ...     name = {"en": "E-mail", "de": "E-Mail"}
    ...     regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    ...     error_msg = {"en": "Not an e-mail address", "de": "Keine E-Mail adresse"}
    ```
    """

    # `name` and `error_msg` are just dicts and get cast to `LocalizedValue` when needed.
    #  This is to not break with the existing API.

    def __init__(self):
        if not all(
            [self.slug, self.regex, self.name, self.error_msg]
        ):  # pragma: no cover
            raise NotImplementedError("Missing properties!")

    def validate(self, value, document):
        if not re.match(self.regex, value):
            raise ValidationError(LocalizedValue(self.error_msg).translate())


class EMailFormatValidator(BaseFormatValidator):
    slug = "email"
    name = {"en": "E-mail", "de": "E-Mail", "fr": "Courriel"}
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    error_msg = {
        "en": "Please enter a valid Email address.",
        "de": "Bitte geben Sie eine gültige E-Mail-Adresse ein.",
        "fr": "Veuillez entrer une addresse e-mail valide.",
    }


class PhoneNumberFormatValidator(BaseFormatValidator):
    slug = "phone-number"
    name = {"en": "Phone number", "de": "Telefonnummer", "fr": "numéro de téléphone"}
    regex = r"^[\s\/\.\(\)-]*(?:\+|0|00)(?:[\s\/\.\(\)-]*\d[\s\/\.\(\)-]*){6,20}$"
    error_msg = {
        "en": "Please enter a valid phone number.",
        "de": "Bitte geben Sie eine gültige Telefonnummer ein.",
        "fr": "Veuillez entrer un numéro de téléphone valide.",
    }


base_format_validators = [EMailFormatValidator, PhoneNumberFormatValidator]


FormatValidator = namedtuple("FormatValidator", ["slug", "name", "regex", "error_msg"])


def get_format_validators(include=None, dic=False):
    """Get all FormatValidators.

    :param include: List of FormatValidators to include
    :param dic: Should return a dict
    :return: List of FormatValidator-objects if dic False otherwise dict
    """

    format_validator_classes = [
        import_string(cls) for cls in settings.FORMAT_VALIDATOR_CLASSES
    ] + base_format_validators
    if include is not None:
        format_validator_classes = [
            fvc for fvc in format_validator_classes if fvc.slug in include
        ]
    if dic:
        return {ds.slug: ds for ds in format_validator_classes}
    return [
        FormatValidator(
            slug=ds.slug,
            name=LocalizedValue(ds.name).translate(),
            regex=ds.regex,
            error_msg=LocalizedValue(ds.error_msg).translate(),
        )
        for ds in format_validator_classes
    ]
