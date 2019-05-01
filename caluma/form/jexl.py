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
        question = segments.pop()
        for segment in segments:
            current_context = current_context.get(segment)

        return current_context.get(question)

    def validate(self, expression):
        return super().validate(expression, QuestionValidatingAnalyzer)
