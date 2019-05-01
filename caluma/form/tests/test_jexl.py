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
        ('"a1"|answer', "A1"),
        ('"parent.form_b.b1"|answer', "B1"),
        ('"parent.form_b.parent.form_a.a1"|answer', "A1"),
    ],
)
def test_jexl_traversal(expression, result):
    form_a = {"a1": "A1"}
    form_b = {"b1": "B1"}
    parent = {"form_a": form_a, "form_b": form_b}
    form_a["parent"] = parent
    form_b["parent"] = parent

    jexl = QuestionJexl(form_a)
    assert jexl.evaluate(expression) == result


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
