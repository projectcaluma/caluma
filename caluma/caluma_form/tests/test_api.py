from caluma.caluma_form.api import save_answer
from caluma.caluma_form.models import Answer
from caluma.caluma_form.validators import AnswerValidator


def test_save_answer_with_context(db, mocker, question_factory, document):
    mocker.patch.object(AnswerValidator, "validate")

    question = question_factory(type="text")
    save_answer(question, document, value="foo", data_source_context={"bar": "baz"})

    answer = Answer.objects.first()
    assert answer.value == "foo"

    AnswerValidator.validate.assert_called_once_with(
        data_source_context={"bar": "baz"},
        document=document,
        instance=None,
        origin=True,
        question=question,
        user=None,
        value="foo",
    )
