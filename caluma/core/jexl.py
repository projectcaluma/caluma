from itertools import count

import pyjexl
from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.exceptions import ParseError
from rest_framework import exceptions


class Cache:
    """Custom cache.

    For JEXL expressions, we cannot use django's cache infrastructure, as the
    cached objects are pickled. This won't work for parsed JEXL expressions, as
    they contain lambdas etc.
    """

    def __init__(self, max_size=2000, evict_to=1500):
        self.max_size = max_size
        self.evict_to = evict_to

        self._cache = {}
        self._mru = {}
        self._mru_count = count()

    def get_or_set(self, key, default):
        if key in self._cache:
            self._mru[key] = next(self._mru_count)
            return self._cache[key]

        ret = self._cache[key] = default()
        self._mru[key] = next(self._mru_count)

        if len(self._mru) > self.max_size:
            self._evict()

        return ret

    def _evict(self):
        to_purge = list(sorted(self._cache.keys(), key=lambda key: self._mru[key]))
        # to_purge contains all keys, but we only want to evict the oldest
        # ones
        num_to_evict = len(to_purge) - self.evict_to

        for key in to_purge[:num_to_evict]:
            del self._cache[key]
            del self._mru[key]


class JexlValidator(object):
    def __init__(self, jexl):
        self.jexl = jexl

    def __call__(self, value):
        errors = list(self.jexl.validate(value))
        if errors:
            raise exceptions.ValidationError(errors)


class JEXL(pyjexl.JEXL):
    expr_cache = Cache()

    def parse(self, expression):
        parsed_expression = self.expr_cache.get_or_set(
            expression, lambda: super(JEXL, self).parse(expression)
        )
        return parsed_expression

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

    def __init__(self, config, transforms=None):
        self.transforms = transforms if transforms else []
        super().__init__(config)

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            # can only extract subject's value if subject is not a transform itself
            if not isinstance(transform.subject, type(transform)):
                yield transform.subject.value
        yield from self.generic_visit(transform)
