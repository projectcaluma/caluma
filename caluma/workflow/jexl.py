from functools import partial
from itertools import chain

from pyjexl import JEXL

from ..core.jexl import ExtractTransformSubjectAnalyzer


class FlowJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("task", lambda spec: spec)
        self.add_transform("tasks", lambda spec: spec)

    def extract_tasks(self, expr):
        yield from self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=["task"])
        )

        # tasks transforms return a list of literals
        yield from [
            literal.value
            for literal in chain(
                *self.analyze(
                    expr, partial(ExtractTransformSubjectAnalyzer, transforms=["tasks"])
                )
            )
        ]
