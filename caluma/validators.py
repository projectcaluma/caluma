from rest_framework import exceptions


class JexlValidator(object):
    def __init__(self, jexl):
        self.jexl = jexl

    def __call__(self, value):
        errors = list(self.jexl.validate(value))
        if errors:
            raise exceptions.ValidationError(errors)
