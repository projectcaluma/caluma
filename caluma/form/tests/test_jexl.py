import pytest

from ..jexl import QuestionJexl


@pytest.mark.parametrize(
    "expression,num_errors",
    [
        # correct case
        ('"question-slug"|answer|mapby', 0),
        # invalid subject type
        ("100|answer", 1),
        # two invalid subject types
        ('["test"]|answer || 1.0|answer', 2),
        # invalid operator
        ("'question-slug1'|answer &&& 'question-slug2'|answer", 1),
    ],
)
def test_question_jexl_validate(expression, num_errors):
    jexl = QuestionJexl()
    assert len(list(jexl.validate(expression))) == num_errors


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[1,2] intersects [2,3]", True),
        ("[1,2] intersects [3,4]", False),
        ("[] intersects []", False),
        ("[1] intersects []", False),
        ("['foo'] intersects ['bar', 'bazz']", False),
        ("['foo'] intersects ['foo', 'foo']", True),
        ("[1] intersects [1] && [2] intersects [2]", True),
        ("[2] intersects [1] + [2]", True),
    ],
)
def test_intersects_operator(expression, result):
    assert QuestionJexl().evaluate(expression) == result


@pytest.mark.parametrize("form__slug", ["f-main-slug"])
def test_jexl_form(db, form):
    answer_by_question = {
        "a1": {"value": "A1", "form": form},
        "b1": {"value": "B1", "form": form},
    }

    assert (
        QuestionJexl({"answers": answer_by_question, "form": form}).evaluate("form")
        == "f-main-slug"
    )


def test_all_deps_hidden(db, form, document_factory, form_question_factory):
    q1 = form_question_factory(form=form, question__is_hidden="true").question
    q2 = form_question_factory(
        form=form,
        question__is_hidden=f"'{q1.slug}'|answer=='blah'",
        question__is_required=f"'{q1.slug}'|answer=='blah'",
    ).question

    qj = QuestionJexl(
        {
            "answers": {},
            "form": form,
            "questions": {q1.slug: q1, q2.slug: q2},
            "all_questions": {q1.slug: q1, q2.slug: q2},
        }
    )
    assert qj.is_hidden(q2)
    assert not qj.is_required(q2)
