from pyjexl import JEXL


class QuestionJexl(JEXL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: add transforms
        # self.add_transform("task", lambda spec: spec)
