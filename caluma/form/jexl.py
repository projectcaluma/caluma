from pyjexl.analysis import ValidatingAnalyzer

from ..core.jexl import JEXL


class QuestionValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "answer" and not isinstance(transform.subject.value, str):
            yield f"{transform.subject.value} is not a valid question slug."

        yield from super().visit_Transform(transform)


class QuestionJexl(JEXL):
    def __init__(self, answer_by_question={}, **kwargs):
        super().__init__(**kwargs)

        self.context = answer_by_question
        self.add_transform("answer", self.answer_transform)
        self.add_transform("mapby", lambda arr, key: [obj[key] for obj in arr])
        self.add_binary_operator(
            "intersects", 20, lambda left, right: any(x in right for x in left)
        )

    def answer_transform(self, question_with_path):
        current_context = self.context
        segments = question_with_path.split(".")

        # Allow question paths to originate from the toplevel (root) document
        if segments[0] == "root":
            while "parent" in current_context:
                current_context = current_context["parent"]
            segments = segments[1:]

        try:
            for segment in segments:
                current_context = current_context[segment]
                current_context = current_context.get('_val', current_context)
            return current_context
        except KeyError:
            explanation = ""
            if len(segments) > 1:
                explanation = f" (failed at segment '{segment}')"

            available_keys = ", ".join(current_context.keys())
            raise RuntimeError(
                f"Question could not be resolved: {question_with_path}{explanation}. Available: {available_keys}"
            )

    def validate(self, expression):
        return super().validate(expression, QuestionValidatingAnalyzer)
