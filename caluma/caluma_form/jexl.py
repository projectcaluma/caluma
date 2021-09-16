from collections import defaultdict
from contextlib import contextmanager
from functools import partial

from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.evaluator import Context

from ..caluma_core.jexl import (
    JEXL,
    ExtractTransformArgumentAnalyzer,
    ExtractTransformSubjectAnalyzer,
    ExtractTransformSubjectAndArgumentsAnalyzer,
)
from .models import Question
from .structure import Field


class QuestionMissing(Exception):
    pass


class QuestionValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "answer" and not isinstance(transform.subject.value, str):
            yield f"{transform.subject.value} is not a valid question slug."

        yield from super().visit_Transform(transform)


class QuestionJexl(JEXL):
    def __init__(self, validation_context=None, **kwargs):

        if validation_context:
            if "jexl_cache" not in validation_context:
                validation_context["jexl_cache"] = defaultdict(dict)
            self._cache = validation_context["jexl_cache"]
        else:
            self._cache = defaultdict(dict)

        super().__init__(**kwargs)

        self._structure = None
        self._form = None

        context_data = None

        if validation_context:
            # cleaned up variant
            self._form = validation_context.get("form")
            self._structure = validation_context.get("structure")
            context_data = {
                "form": self._form.slug if self._form else None,
                "info": self._structure,
            }

        self.context = Context(context_data)

        self.add_transform("answer", self.answer_transform)

    def answer_transform(self, question_slug, *args):
        field = self._structure.get_field(question_slug)

        # The first and only argument is the default value. If passed the field
        # is not required and we return that argument.
        if not field and len(args):
            return args[0]

        if self.is_hidden(field):
            return field.question.empty_value()

        # This overrides the logic in field.value() to consider visibility for
        # table cells
        elif field.question.type == Question.TYPE_TABLE and field.answer is not None:
            return [
                {
                    cell.question.slug: cell.value()
                    for cell in row.children()
                    if not self.is_hidden(cell)
                }
                for row in field.children()
            ]

        return field.value()

    def validate(self, expression, **kwargs):
        return super().validate(expression, QuestionValidatingAnalyzer)

    def extract_referenced_questions(self, expr):
        transforms = ["answer"]
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=transforms)
        )

    def extract_referenced_questions_with_arguments(self, expr):
        transforms = ["answer"]
        yield from self.analyze(
            expr,
            partial(ExtractTransformSubjectAndArgumentsAnalyzer, transforms=transforms),
        )

    def extract_referenced_mapby_questions(self, expr):
        transforms = ["mapby"]
        yield from self.analyze(
            expr, partial(ExtractTransformArgumentAnalyzer, transforms=transforms)
        )

    @contextmanager
    def use_field_context(self, field: Field):
        """Context manger to temporarily overwrite self._structure.

        This is used so we can evaluate each JEXL expression in the context
        of the corresponding question, not from where the question was
        referenced.
        This is relevant in table questions and form questions, so we always
        lookup the correct answer value (no "crosstalk" between rows, for example)
        """

        # field's parent is the fieldset - which is a valid structure object
        old_structure = self._structure
        self._structure = field.parent() or self._structure
        yield
        self._structure = old_structure

    def _get_referenced_fields(self, field: Field, expr: str):
        deps = list(self.extract_referenced_questions_with_arguments(expr))
        referenced_fields = [self._structure.get_field(slug) for slug, _ in deps]

        referenced_slugs = [ref.question.slug for ref in referenced_fields if ref]

        for slug, args in deps:
            required = len(args) == 0
            if slug not in referenced_slugs and required:
                raise QuestionMissing(
                    f"Question `{slug}` could not be found in form {field.form}"
                )

        return [field for field in referenced_fields if field]

    def is_hidden(self, field: Field):
        """Return True if the given field is hidden.

        This checks whether the dependency questions are hidden, then
        evaluates the field's is_hidden expression itself.
        """
        cache_key = (field.document.pk, field.question.pk)

        if cache_key in self._cache["hidden"]:
            return self._cache["hidden"][cache_key]

        # Check visibility of dependencies before actually evaluating the `is_hidden`
        # expression. If all dependencies are hidden,
        # there is no way to evaluate our own visibility, so we default to
        # hidden state as well.
        referenced_fields = self._get_referenced_fields(field, field.question.is_hidden)

        # all() returns True for the empty set, thus we need to
        # check that we have some deps at all first
        all_deps_hidden = bool(referenced_fields) and all(
            self.is_hidden(ref_field) for ref_field in referenced_fields
        )
        if all_deps_hidden:
            self._cache["hidden"][cache_key] = True
            return True

        # Also check if the question is hidden indirectly,
        # for example via parent formquestion.
        parent = field.parent()
        if parent and parent.question and self.is_hidden(parent):
            # no way this is shown somewhere
            self._cache["hidden"][cache_key] = True
            return True

        # if the question is visible-in-context and not hidden by invisible dependencies,
        # we can evaluate it's own is_hidden expression
        with self.use_field_context(field):
            self._cache["hidden"][cache_key] = self.evaluate(field.question.is_hidden)

        return self._cache["hidden"][cache_key]

    def is_required(self, field: Field):
        cache_key = (field.document.pk, field.question.pk)
        question = field.question

        if cache_key in self._cache["required"]:
            return self._cache["required"][cache_key]

        referenced_fields = self._get_referenced_fields(field, question.is_required)

        # all() returns True for the empty set, thus we need to
        # check that we have some deps at all first
        all_deps_hidden = bool(referenced_fields) and all(
            self.is_hidden(ref_field) for ref_field in referenced_fields
        )
        if all_deps_hidden:
            ret = False
        else:
            with self.use_field_context(field):
                ret = self.evaluate(question.is_required)
        self._cache["required"][cache_key] = ret
        return ret

    def evaluate(self, expr, raise_on_error=True):
        try:
            return super().evaluate(expr)
        except TypeError:
            if raise_on_error:
                raise
            return None
