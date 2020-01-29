from collections import defaultdict
from functools import partial

from django.db.models import Q
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

        context_data = None
        if validation_context:
            context_data = {**validation_context}
            form = validation_context.get("form")
            if form:
                context_data["form"] = form.slug

        self.context = Context(context_data)

        self.add_transform("answer", self.answer_transform)
        self.add_transform("mapby", lambda arr, key: [obj[key] for obj in arr])
        self.add_binary_operator(
            "intersects", 20, lambda left, right: any(x in right for x in left)
        )

    def answer_transform(self, question):

        aq = self.context["structure"].get_ans_question(question)
        if aq is None:
            raise QuestionMissing(
                f"Question `{question}` could not be found in form {self.context['form']}"
            )

        return aq.ans_value()

    def validate(self, expression, **kwargs):
        return super().validate(expression, QuestionValidatingAnalyzer)

    def extract_referenced_questions(self, expr):
        transforms = ["answer", "mapby"]
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=transforms)
        )

    def _question(self, slug):
        ans_question = self.context["structure"].get_ans_question(slug)
        if ans_question:
            return ans_question.question

        raise QuestionMissing(
            f"Question `{slug}` could not be found in form {self.context['form']}"
        )

    def _paths_to_question(self, question, doc_form):
        """Return all paths from the doc form to the given question."""
        cache = self._cache["containers_hidden_paths"]
        cache_key = (doc_form.slug, question.slug)

        if cache_key in cache:
            return cache[cache_key]

        res = []
        if doc_form in question.forms.all():
            # found a path - add it to our result list
            res.append([question])

        parent_questions = Question.objects.filter(
            Q(type=Question.TYPE_FORM) | Q(type=Question.TYPE_TABLE),
            Q(sub_form__questions__pk=question) | Q(row_form__questions__pk=question),
        )
        for parent_question in parent_questions:
            res.extend(
                [
                    path + [question]
                    for path in self._paths_to_question(parent_question, doc_form)
                ]
            )

        cache[cache_key] = res
        return res

    def _all_containers_hidden(self, question):
        """Check whether all containers of the given question are hidden.

        The question could be used in multiple sub-forms in the given
        document structure. This goes through all paths from the main form
        to the given question, and checks if they're hidden.

        If all subforms are hidden where the question shows up,
        the question shall be hidden as well.
        """
        paths = self._paths_to_question(question, self.context.get("document").form)

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

    def is_hidden(self, question):
        """Return True if the given question is hidden.

        This checks whether the dependency questions are hidden, then
        evaluates the question's is_hidden expression itself.
        """
        if question.pk in self._cache["hidden"]:
            return self._cache["hidden"][question.pk]
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
            self._cache["hidden"][question.pk] = True
            return True

        # Also check if the question is hidden indirectly,
        # for example via parent formquestion.
        if self._all_containers_hidden(question):
            # no way this is shown somewhere
            self._cache["hidden"][question.pk] = True
            return True
        # if the question is visible-in-context and not hidden by invisible dependencies,
        # we can evaluate it's own is_hidden expression
        self._cache["hidden"][question.pk] = self.evaluate(question.is_hidden)
        return self._cache["hidden"][question.pk]

    def is_required(self, question):
        if question.pk in self._cache["required"]:
            return self._cache["required"][question.pk]

        deps = list(self.extract_referenced_questions(question.is_required))

        if bool(deps) and all(self.is_hidden(self._question(dep)) for dep in deps):
            # all dependent questions are hidden. cannot evaluate,
            # so assume requiredness to be False
            ret = False
        else:
            ret = self.evaluate(question.is_required)
        self._cache["required"][question.pk] = ret
        return ret
