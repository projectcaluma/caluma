import functools

import pytest
from pyjexl import JEXL

from ..jexl import Cache, ExtractTransformSubjectAnalyzer


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


def test_jexl_cache():
    cache = Cache(20, 10)

    # fill the cache "to the brim"
    for x in range(19):
        cache.get_or_set(x, lambda: x)
    assert len(cache._mru) == 19
    assert len(cache._cache) == 19

    # insert last element before eviction
    cache.get_or_set("x", lambda: "x")
    assert len(cache._mru) == 20
    assert len(cache._cache) == 20

    # one more - this should trigger eviction
    cache.get_or_set("y", lambda: "y")
    assert len(cache._mru) == 10
    assert len(cache._cache) == 10

    # now make sure the right entries were evicted
    for x in range(10):
        assert x not in cache._cache
        assert x not in cache._mru

    # validate invariants
    assert cache._cache.keys() == cache._mru.keys()
