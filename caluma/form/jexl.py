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

    def answer_transform(self, *args):
        question = args[0]
        path = args[1] if len(args) > 1 else None

        current_context = self.context
        if path:
            parts = path.split(".")
            for part in parts:
                current_context = current_context.get(part)

        return current_context.get(question)

    def validate(self, expression):
        return super().validate(expression, QuestionValidatingAnalyzer)
