import functools

import pytest
from pyjexl import JEXL

from ..jexl import ExtractTransformSubjectAnalyzer


@pytest.mark.parametrize(
    "expression, expected_transforms",
    [
        ('63 > 62 ? "test"|transform1 : "test2"|transform2', {"test"}),
        ('63 > 62 ? "test"|transform1 : "test2"|transform1', {"test", "test2"}),
        ('"test2"|transform2', set()),
        ('"test2"|transform1', {"test2"}),
    ],
)
def test_extract_transforms(expression, expected_transforms):
    jexl = JEXL()
    jexl.add_transform("transform1", lambda x: x)
    jexl.add_transform("transform2", lambda x: x)

    assert set(
        jexl.analyze(
            expression,
            functools.partial(
                ExtractTransformSubjectAnalyzer, transforms=["transform1"]
            ),
        )
    ) == set(expected_transforms)
