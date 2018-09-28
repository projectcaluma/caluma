from functools import partial

from pyjexl import JEXL

from ..jexl import ExtractTransformSubjectAnalyzer


class FlowJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("taskSpecification", lambda spec: spec)

    def extract_task_specifications(self, expr):
        return self.analyze(
            expr,
            partial(ExtractTransformSubjectAnalyzer, transforms=["taskSpecification"]),
        )
