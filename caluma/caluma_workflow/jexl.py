from functools import partial
from itertools import chain

from pyjexl.analysis import ValidatingAnalyzer
from pyjexl.evaluator import Context

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
    """
    Class for evaluating GroupJexl.

    validation_context is expected to be the following:

    {
        "case": {
            "created_by_group": str,
        },
        "work_item": {
            "created_by_group": str,
        },
        "prev_work_item": {
            "controlling_groups": list of str,
        },
    }
    """

    def __init__(self, validation_context=None, **kwargs):
        super().__init__(**kwargs)

        context_data = None

        if validation_context:
            context_data = {"info": validation_context}

        self.context = Context(context_data)
        self.add_transform("groups", lambda spec: spec)

    def validate(self, expression):
        return super().validate(expression, GroupValidatingAnalyzer)

    def evaluate(self, expression, context=None):
        value = super().evaluate(expression, context)
        if isinstance(value, list) or value is None:
            return value
        return [value]


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
