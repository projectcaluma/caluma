from functools import partial

from pyjexl import JEXL

from ..core.jexl import ExtractTransformSubjectAnalyzer


class FlowJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("task", lambda spec: spec)

    def extract_tasks(self, expr):
        return self.analyze(
            expr, partial(ExtractTransformSubjectAnalyzer, transforms=["task"])
        )
