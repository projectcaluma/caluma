import json
import math
import numbers
from functools import partial
from itertools import count
from logging import getLogger

import pyjexl
from pyjexl.analysis import JEXLAnalyzer, ValidatingAnalyzer
from pyjexl.exceptions import ParseError
from pyjexl.parser import ArrayLiteral, Literal, ObjectLiteral
from rest_framework import exceptions

log = getLogger(__name__)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_transform("debug", self._debug_transform)
        self._expr_stack = []

        self.add_transform("mapby", self._mapby_transform)
        self.add_transform("stringify", lambda obj: json.dumps(obj))
        self.add_binary_operator(
            "intersects", 20, lambda left, right: any(x in right for x in left)
        )

        def _handle_error(func, subject, *args):
            try:
                if not args:
                    return func(subject)
                return func(subject, *args)
            except (TypeError, ValueError, ZeroDivisionError):
                return None

        def _handle_error_with_filter(func, subject, *args):
            return _handle_error(
                func,
                [
                    s
                    for s in subject
                    if isinstance(s, numbers.Number) and not math.isnan(s)
                ],
                *args,
            )

        # list operations
        self.add_transform("min", partial(_handle_error_with_filter, min))
        self.add_transform("max", partial(_handle_error_with_filter, max))
        self.add_transform("sum", partial(_handle_error_with_filter, sum))
        self.add_transform(
            "avg",
            partial(_handle_error_with_filter, lambda arr: sum(arr) / len(arr)),
        )
        # float operations
        self.add_transform("ceil", partial(_handle_error, math.ceil))
        self.add_transform("floor", partial(_handle_error, math.floor))
        self.add_transform(
            "round",
            partial(
                _handle_error,
                self._round_compat,
            ),
        )

    def _round_compat(self, num, ndigits=0):
        power = 10**ndigits
        return float(math.floor((num * power) + 0.5) / power)

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

    def _debug_transform(self, value, label=None):
        expr = self._expr_stack[-1]

        log.info(
            f"JEXL debug ({label}): value = `{value}`"
            if label
            else f"JEXL debug: in expression `{expr}`, value = `{value}`"
        )
        return value

    def _mapby_transform(self, arr, *keys):
        if not isinstance(arr, list):
            return None

        return [
            [obj.get(key) for key in keys] if len(keys) > 1 else obj.get(keys[0])
            for obj in arr
        ]

    def evaluate(self, expression, context=None):
        self._expr_stack.append(expression)
        try:
            return super().evaluate(expression, context)
        finally:
            self._expr_stack.pop()


class CalumaAnalyzer(JEXLAnalyzer):
    """Analyzer visiting Object and ArrayLiterals.

    TODO: Upstream this.
    """

    def __init__(self, config, transforms=None):
        self.transforms = transforms if transforms else []
        super().__init__(config)

    def generic_visit(self, expression):
        for child in expression.children:
            assert child is not None
            for c in self.visit(child):
                yield c

        if isinstance(expression, ArrayLiteral):
            for child in expression.value:
                assert child is not None
                for c in self.visit(child):
                    yield c

        elif isinstance(expression, ObjectLiteral):
            for child in expression.value.values():
                assert child is not None
                for c in self.visit(child):
                    yield c


class ExtractTransformSubjectAnalyzer(CalumaAnalyzer):
    """
    Extract all referenced subjects of given transforms.

    If no transforms are given all references of all transforms will be extracted.
    """

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            # can only extract subject's value if subject is a Literal
            if not isinstance(transform.subject, type(transform)):
                yield transform.subject.value

        yield from self.generic_visit(transform)


class ExtractTransformArgumentAnalyzer(CalumaAnalyzer):
    """
    Extract all referenced arguments of given transforms.

    If no transforms are given all references of all transforms will be extracted.
    """

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            # "mapby" is the only transform that accepts args, those can hold
            # references. We need a "lookahead" to peek if the subject is an
            # answer transform in this case we assume the arguments are
            # references (as opposed to simple literals)
            if (
                transform.name == "mapby"
                and transform.subject
                and transform.subject.name == "answer"
                and len(transform.args)
            ):
                for arg in transform.args:
                    if isinstance(arg, Literal):
                        yield arg.value

        yield from self.generic_visit(transform)


class ExtractTransformSubjectAndArgumentsAnalyzer(CalumaAnalyzer):
    """
    Extract all referenced subjects and arguments of a given transforms.

    If no transforms are given all references of all transforms will be extracted.
    """

    def visit_Transform(self, transform):
        if not self.transforms or transform.name in self.transforms:
            if not isinstance(transform.subject, type(transform)):
                yield (transform.subject.value, transform.args)

        yield from self.generic_visit(transform)
