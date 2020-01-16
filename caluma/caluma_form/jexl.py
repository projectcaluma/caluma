from functools import partial

from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.evaluator import Context

from ..caluma_core.jexl import JEXL, ExtractTransformSubjectAnalyzer


class QuestionMissing(Exception):
    pass


class QuestionValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "answer" and not isinstance(transform.subject.value, str):
            yield f"{transform.subject.value} is not a valid question slug."

        yield from super().visit_Transform(transform)


class QuestionJexl(JEXL):
    def __init__(self, validation_context=None, **kwargs):
        answer_by_question = validation_context["answers"] if validation_context else {}

        super().__init__(**kwargs)

        context_data = None
        if validation_context:
            context_data = {**validation_context}
            form = validation_context.get("form")
            if form:
                context_data["form"] = form.slug

        self.context = Context(context_data)
        self.answer_by_question = answer_by_question

        self.add_transform("answer", self.answer_transform)
        self.add_transform("mapby", lambda arr, key: [obj[key] for obj in arr])
        self.add_binary_operator(
            "intersects", 20, lambda left, right: any(x in right for x in left)
        )

    def answer_transform(self, question):
        try:
            return self.answer_by_question[question]
        except KeyError:  # pragma: no cover
            raise QuestionMissing(
                f"Question `{question}` could not be found in form {self.context['form']}"
            )

    def validate(self, expression, **kwargs):
        return super().validate(expression, QuestionValidatingAnalyzer)

    def extract_referenced_questions(self, expr):
        transforms = ["answer", "mapby"]
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=transforms)
        )

    def _question(self, slug):
        question = self.context["questions"].get(
            slug, self.context["all_questions"].get(slug)
        )
        if not question:
            raise QuestionMissing(
                f"Question `{slug}` could not be found in form {self.context['form']}"
            )
        return question

    def is_hidden(self, question):
        """Return True if the given question is hidden.

        This checks whether the dependency questions are hidden, then
        evaluates the question's is_hidden expression itself.
        """
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

        return all_deps_hidden or self.evaluate(question.is_hidden)

    def is_required(self, question):
        deps = list(self.extract_referenced_questions(question.is_required))

        if bool(deps) and all(self.is_hidden(self._question(dep)) for dep in deps):
            # all dependent questions are hidden. cannot evaluate,
            # so assume requiredness to be False
            return False

        return self.evaluate(question.is_required)
