from pyjexl import JEXL


class FlowJexl(JEXL):
    def __init__(self, workflow_specification=None, **kwargs):
        super().__init__(**kwargs)
        self.add_transform("taskSpecification", lambda spec: spec)
