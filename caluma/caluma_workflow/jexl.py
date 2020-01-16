from functools import partial
from itertools import chain

from pyjexl.analysis import ValidatingAnalyzer

from ..caluma_core.jexl import JEXL, ExtractTransformSubjectAnalyzer


class GroupValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "groups" and not isinstance(transform.subject.value, list):
            yield f"{transform.subject.value} is not a valid list of groups."

        yield from super().visit_Transform(transform)


class TaskValidatingAnalyzer(ValidatingAnalyzer):
    def visit_Transform(self, transform):
        if transform.name == "tasks" and not isinstance(transform.subject.value, list):
            yield f"{transform.subject.value} is not a valid list of tasks."

        if transform.name == "task" and not isinstance(transform.subject.value, str):
            yield f"{transform.subject.value} is not a valid task slug."

        yield from super().visit_Transform(transform)


class GroupJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("groups", lambda spec: spec)

    def validate(self, expression):
        return super().validate(expression, GroupValidatingAnalyzer)


class FlowJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("task", lambda spec: spec)
        self.add_transform("tasks", lambda spec: spec)

    def validate(self, expression):
        return super().validate(expression, TaskValidatingAnalyzer)

    def extract_tasks(self, expr):
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=["task"])
        )

        # tasks transforms return a list of literals
        yield from (
            literal.value
            for literal in chain(
                *self.analyze(
                    expr, partial(ExtractTransformSubjectAnalyzer, transforms=["tasks"])
                )
            )
        )
