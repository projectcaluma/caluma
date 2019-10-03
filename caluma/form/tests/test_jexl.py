# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

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


def test_jexl_form():
    answer_by_question = {
        "a1": {"value": "A1", "form": "f-main-slug"},
        "b1": {"value": "B1", "form": "f-main-slug"},
    }

    assert (
        QuestionJexl(answer_by_question, "f-main-slug").evaluate("form")
        == "f-main-slug"
    )
