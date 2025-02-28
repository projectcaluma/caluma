import weakref
from collections import ChainMap
from functools import partial

from pyjexl.analysis import ValidatingAnalyzer

from caluma.caluma_core.exceptions import QuestionMissing

from ..caluma_core.jexl import (
    JEXL,
    ExtractTransformArgumentAnalyzer,
    ExtractTransformSubjectAnalyzer,
)

"""
Form JEXL handling

Design principles:

* The JEXL classes do not deal with context switching between questions.
  Where needed, we ask the corresponding field from the structure to give us
  the necessary information.
* The QuestionJexl class only sets up the "runtime", any context is used from
  the structure code.
* We only deal with the *evaluation*, no transform/extraction is happening here
* Caching is done by the structure code, not here
* JEXL evaluation happens lazily, but the results are cached.
"""


class QuestionValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "answer" and not isinstance(transform.subject.value, str):
            yield f"{transform.subject.value} is not a valid question slug."

        yield from super().visit_Transform(transform)


class QuestionJexl(JEXL):
    def __init__(self, field, **kwargs):
        """Initialize QuestionJexl.

        Note: The field *may* be set to `None` if you're intending
        to use the object for expression analysis only (exctract_* methods
        for example)
        """
        super().__init__(**kwargs)
        self.field = weakref.proxy(field) if field else None

        self.add_transform("answer", self.answer_transform)

    def answer_transform(self, question_slug, *args):
        field = self.field.get_field(question_slug)

        def _default_or_empty():
            if len(args):
                return args[0]
            return field.question.empty_value()

        if not field:
            if args:
                return args[0]
            else:
                # No default arg, so we must raise an exception
                raise QuestionMissing(
                    f"Question `{question_slug}` could not be found in form {self.field.get_form()}"
                )

        if field.is_hidden():
            # Hidden fields *always* return the empty value, even if we have
            # a default
            return field.question.empty_value()
        elif field.is_empty():
            # not hidden, but empty
            return _default_or_empty()

        return field.get_value()

    def validate(self, expression, **kwargs):
        return super().validate(expression, QuestionValidatingAnalyzer)

    def extract_referenced_questions(self, expr):
        transforms = ["answer"]
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=transforms)
        )

    def extract_referenced_mapby_questions(self, expr):
        transforms = ["mapby"]
        yield from self.analyze(
            expr, partial(ExtractTransformArgumentAnalyzer, transforms=transforms)
        )

    def evaluate(self, expr, raise_on_error=True):
        try:
            return super().evaluate(expr, ChainMap(self.context))
        except (
            TypeError,
            ValueError,
            ZeroDivisionError,
            AttributeError,
        ):
            if raise_on_error:
                raise
            return None
