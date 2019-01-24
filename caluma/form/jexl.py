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

        self.add_transform("answer", lambda question: answer_by_question.get(question))
        self.add_transform("mapby", lambda arr, key: [obj[key] for obj in arr])

    def validate(self, expression):
        return super().validate(expression, QuestionValidatingAnalyzer)
