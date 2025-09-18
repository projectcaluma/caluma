import re
from collections import namedtuple
from warnings import warn

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from graphql.error import GraphQLError
from localized_fields.value import LocalizedValue

from caluma.caluma_form.models import Question
from caluma.deprecation import CalumaDeprecationWarning

FORMAT_VALIDATION_FAILED = "format_validation_failed"


def translate(text):
    if isinstance(text, dict):
        return LocalizedValue(text).translate()

    return str(text)


class BaseFormatValidator:
    r"""Basic format validator class to be extended by any format validator implementation.

    A custom format validator class could look like this:

    ```
    >>> from caluma.caluma_form.format_validators import BaseFormatValidator
    ... from django.utils.translation import gettext_lazy as _
    ...
    ...
    ... class CustomFormatValidator(BaseFormatValidator):
    ...     slug = "email"
    ...     name = _("E-mail")
    ...     regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    ...     error_msg = _("Not an e-mail address")
    ```

    If your format validator can't be implemented using a regex, you may also
    implement a custom `is_valid` class method yourself. The method takes two
    arguments, the value that is being validated and the document as context for
    more elaborate validations:

    ```
    >>> from caluma.caluma_form.format_validators import BaseFormatValidator
    ... from django.utils.translation import gettext_lazy as _
    ...
    ...
    ... class CustomFormatValidator(BaseFormatValidator):
    ...     slug = "even-date"
    ...     name = _("Even date")
    ...     error_msg = _("Not an even date")
    ...
    ...     @classmethod
    ...     def is_valid(cls, value, document, question):
    ...         return value.day() % 2 == 0
    ```
    """

    regex = None
    allowed_question_types = [Question.TYPE_TEXT, Question.TYPE_TEXTAREA]

    def __init_subclass__(cls, **kwargs):
        for prop in ["slug", "name", "error_msg"]:  # pragma: no cover
            if not hasattr(cls, prop):
                # Make sure that `slug`, `name` and `error_msg` are
                # defined properties on the class inheriting from this base
                # class
                raise NotImplementedError(
                    f"{cls.__name__} is missing required property `{prop}`"
                )

        for prop in ["name", "error_msg"]:
            if isinstance(getattr(cls, prop), dict):
                # Previously, inheriting classes could define a dictionary with
                # locale codes as keys and the respective translation for that
                # locale in the value. This behaviour was deprecated in favour
                # of using lazy translations with gettext.
                warn(
                    f"{cls.__name__}: Defining `{prop}` as dictionary is deprecated. Please use `django.utils.translation.gettext_lazy` instead.",
                    CalumaDeprecationWarning,
                )

    @classmethod
    def validate(cls, value, document, question):
        if not cls.is_valid(value, document, question):
            raise GraphQLError(
                translate(
                    cls.error_msg % cls.get_error_msg_args(value, document, question)
                ),
                extensions={"code": FORMAT_VALIDATION_FAILED},
            )

    @classmethod
    def is_valid(cls, value, document, question):
        if not cls.regex:  # pragma: no cover
            raise NotImplementedError("Property `regex` is missing")

        return re.match(cls.regex, value)

    @classmethod
    def get_error_msg_args(cls, value, document, question):
        return dict(value=value)


class EMailFormatValidator(BaseFormatValidator):
    slug = "email"
    name = _("E-mail address")
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    error_msg = _("Please enter a valid e-mail address")


class PhoneNumberFormatValidator(BaseFormatValidator):
    slug = "phone-number"
    name = _("Phone number")
    regex = r"^[\s\/\.\(\)-]*(?:\+|0|00)(?:[\s\/\.\(\)-]*\d[\s\/\.\(\)-]*){6,20}$"
    error_msg = _("Please enter a valid phone number")


base_format_validators = [EMailFormatValidator, PhoneNumberFormatValidator]


FormatValidator = namedtuple(
    "FormatValidator", ["slug", "name", "regex", "allowed_question_types"]
)


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
            name=translate(ds.name),
            regex=ds.regex,
            allowed_question_types=ds.allowed_question_types,
        )
        for ds in format_validator_classes
    ]
