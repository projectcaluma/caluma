import functools

import pyjexl
import pytest

from ..jexl import JEXL, Cache, ExtractTransformSubjectAnalyzer


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
    jexl = pyjexl.JEXL()
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


@pytest.mark.parametrize(
    "expression, expected_log, expected_output",
    [
        ("'foo'", [], "foo"),
        (
            "'foo'|debug",
            ["JEXL debug: in expression `'foo'|debug`, value = `foo`"],
            "foo",
        ),
        (
            "'foo'|debug|debug",
            [
                "JEXL debug: in expression `'foo'|debug|debug`, value = `foo`",
                "JEXL debug: in expression `'foo'|debug|debug`, value = `foo`",
            ],
            "foo",
        ),
        (
            "'\"bar\"|debug'|sub_expr|debug",
            [
                'JEXL debug: in expression `"bar"|debug`, value = `bar`',
                "JEXL debug: in expression `'\"bar\"|debug'|sub_expr|debug`, value = `bar`",
            ],
            "bar",
        ),
        (
            "'hello world'|debug('The world debugger')",
            ["JEXL debug (The world debugger): value = `hello world`"],
            "hello world",
        ),
    ],
)
def test_debug_transform(expression, expected_log, expected_output, caplog):
    jexl = JEXL()

    def sub_expr(val):
        return jexl.evaluate(val)

    jexl.add_transform("sub_expr", sub_expr)

    assert jexl.evaluate(expression) == expected_output
    assert caplog.messages == expected_log


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
