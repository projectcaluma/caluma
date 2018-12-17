from pyjexl import JEXL


class QuestionJexl(JEXL):
    def __init__(self, answer_by_question={}, **kwargs):
        super().__init__(**kwargs)

        self.add_transform("answer", lambda question: answer_by_question.get(question))
