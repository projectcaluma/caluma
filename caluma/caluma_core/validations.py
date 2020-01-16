import inspect
from functools import wraps

from django.core.exceptions import ImproperlyConfigured

from .collections import list_duplicates


def validation_for(mutation):
    """Decorate function to overwriting validation of specific mutation."""

    def decorate(fn):
        @wraps(fn)
        def _decorated(self, mutation, data, info):
            return fn(self, mutation, data, info)

        _decorated._validation = mutation
        return _decorated

    return decorate


class BaseValidation(object):
    """Basic validation class to be extended by any validation implementation.

    In combination with the decorators `@validation_for` a custom validation class
    can define validations for specific mutations.
    It is also possible to execute the same validation logic for all mutations
    using the base class `Mutation`.

    A custom validation class could look like this:
    ```
    >>> from caluma.caluma_form.schema import SaveForm
    ... from caluma.mutation import Mutation
    ... from rest_framework import exceptions
    ...
    ... class CustomValidation(BaseValidation):
    ...     @validation_for(Mutation)
    ...     def validate_mutation(self, mutation, data, info):
    ...         # add your default specific validation code here
    ...         return data
    ...
    ...     @validation_for(SaveForm)
    ...     def validate_save_form(self, mutation, data, info):
    ...         if data['meta'] and info.context.group != 'admin':
    ...           raise exceptions.ValidationException('May not change meta on form')
    ...         return data
    """

    def __init__(self):
        validation_fns = inspect.getmembers(self, lambda m: hasattr(m, "_validation"))
        validation_muts = [fn._validation.__name__ for _, fn in validation_fns]
        validation_muts_dups = list_duplicates(validation_muts)
        if validation_muts_dups:
            raise ImproperlyConfigured(
                f"`validation_for` defined multiple times for "
                f"{', '.join(validation_muts_dups)} in {str(self)}"
            )
        self._validations = {fn._validation: fn for _, fn in validation_fns}

    def validate(self, mutation, data, info):
        for cls in mutation.mro():
            if cls in self._validations:
                return self._validations[cls](mutation, data, info)
        return data
