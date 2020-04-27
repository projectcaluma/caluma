from collections import defaultdict
from contextlib import contextmanager
from functools import partial

from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.evaluator import Context

from ..caluma_core.jexl import JEXL, ExtractTransformSubjectAnalyzer
from .models import Question


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
        self.add_transform(
            "mapby", lambda arr, key: [obj.get(key, None) for obj in arr]
        )
        self.add_binary_operator(
            "intersects", 20, lambda left, right: any(x in right for x in left)
        )

    def answer_transform(self, question_slug):
        question = self._question(question_slug)

        if self.is_hidden(question):
            if question.type in [
                Question.TYPE_MULTIPLE_CHOICE,
                Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
                Question.TYPE_TABLE,
            ]:
                return []

            return None

        return self._structure.get_field(question_slug).value()

    def validate(self, expression, **kwargs):
        return super().validate(expression, QuestionValidatingAnalyzer)

    def extract_referenced_questions(self, expr):
        transforms = ["answer", "mapby"]
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=transforms)
        )

    def _question(self, slug):
        field = self._structure.get_field(slug)
        if field:
            return field.question

        raise QuestionMissing(
            f"Question `{slug}` could not be found in form {self.context['form']}"
        )

    @contextmanager
    def use_question_context(self, question_slug):
        """Context manger to temporarily overwrite self._structure.

        This is used so we can evaluate each JEXL expression in the context
        of the corresponding question, not from where the question was
        referenced.
        This is relevant in table questions and form questions, so we always
        lookup the correct answer value (no "crosstalk" between rows, for example)
        """

        # field's parent is the fieldset - which is a valid structure object
        old_structure = self._structure
        self._structure = self._structure.get_field(question_slug).parent()
        yield
        self._structure = old_structure

    def _all_containers_hidden(self, question):
        """Check whether all containers of the given question are hidden.

        The question could be used in multiple sub-forms in the given
        document structure. This goes through all paths from the main form
        to the given question, and checks if they're hidden.

        If all subforms are hidden where the question shows up,
        the question shall be hidden as well.
        """
        paths = self._structure.root().paths_to_question(question.slug)

        res = bool(paths) and all(
            # the "inner" check here represents a single path. If any
            # question is hidden, the question is not reachable via
            # this path
            bool(path) and any(self.is_hidden(fq) for fq in path if fq != question)
            for path in paths
        )
        # The outer check verifies if all paths are "hidden" (ie have a hidden
        # question in them). If all paths from the root form to the
        # question are hidden, the question must indeed be hidden itself.

        return res

    def _cache_key(self, question_slug):
        field = self._structure.get_field(question_slug)
        return (field.document.pk, question_slug)

    def is_hidden(self, question):
        """Return True if the given question is hidden.

        This checks whether the dependency questions are hidden, then
        evaluates the question's is_hidden expression itself.
        """
        cache_key = self._cache_key(question.pk)

        if cache_key in self._cache["hidden"]:
            return self._cache["hidden"][cache_key]
        # Check visibility of dependencies before actually evaluating the `is_hidden`
        # expression. If all dependencies are hidden,
        # there is no way to evaluate our own visibility, so we default to
        # hidden state as well.

        deps = list(self.extract_referenced_questions(question.is_hidden))

        # all() returns True for the empty set, thus we need to
        # check that we have some deps at all first
        all_deps_hidden = bool(deps) and all(
            self.is_hidden(self._question(dep)) for dep in deps
        )
        if all_deps_hidden:
            self._cache["hidden"][cache_key] = True
            return True

        # Also check if the question is hidden indirectly,
        # for example via parent formquestion.
        if self._all_containers_hidden(question):
            # no way this is shown somewhere
            self._cache["hidden"][cache_key] = True
            return True
        # if the question is visible-in-context and not hidden by invisible dependencies,
        # we can evaluate it's own is_hidden expression

        with self.use_question_context(question.pk):
            self._cache["hidden"][cache_key] = self.evaluate(question.is_hidden)
        return self._cache["hidden"][cache_key]

    def is_required(self, question_field):
        cache_key = (question_field.document.pk, question_field.question.pk)
        question = question_field.question

        if cache_key in self._cache["required"]:
            return self._cache["required"][cache_key]

        deps = list(self.extract_referenced_questions(question.is_required))

        if bool(deps) and all(self.is_hidden(self._question(dep)) for dep in deps):
            # all dependent questions are hidden. cannot evaluate,
            # so assume requiredness to be False
            ret = False
        else:
            with self.use_question_context(question.pk):
                ret = self.evaluate(question.is_required)
        self._cache["required"][cache_key] = ret
        return ret
