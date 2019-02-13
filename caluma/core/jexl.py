import pyjexl
from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.exceptions import ParseError
from rest_framework import exceptions


class JexlValidator(object):
    def __init__(self, jexl):
        self.jexl = jexl

    def __call__(self, value):
        errors = list(self.jexl.validate(value))
        if errors:
            raise exceptions.ValidationError(errors)


class JEXL(pyjexl.JEXL):
    def validate(self, expression, ValidatingAnalyzerClass=ValidatingAnalyzer):
        try:
            for res in self.analyze(expression, ValidatingAnalyzerClass):
                yield res
        except ParseError as err:
            yield str(err)


class ExtractTransformSubjectAnalyzer(ValidatingAnalyzer):
    """
    Extract all subject values of given transforms.

    If no transforms are given all subjects of all transforms will be extracted.
    """

    def __init__(self, config, transforms=[]):
        self.transforms = transforms
        super().__init__(config)

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            yield transform.subject.value
        yield from self.generic_visit(transform)
