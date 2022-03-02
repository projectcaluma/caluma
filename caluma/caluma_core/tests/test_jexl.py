import functools

import pyjexl
import pytest

from ..jexl import JEXL, Cache, CalumaAnalyzer, ExtractTransformSubjectAnalyzer


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

    assert (
        set(
            jexl.analyze(
                expression,
                functools.partial(
                    ExtractTransformSubjectAnalyzer, transforms=["transform1"]
                ),
            )
        )
        == set(expected_transforms)
    )


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


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[{ key: 1 }]|mapby('key')", [1]),
        ("[{ otherkey: 1 }]|mapby('key')", [None]),
        ("[]|mapby('key')", []),
        ("[{ a: 1, b: 2 }]|mapby('a', 'b', 'c')", [[1, 2, None]]),
        ("0|mapby('key')", None),
    ],
)
def test_mapby_operator(expression, result):
    assert JEXL().evaluate(expression) == result


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
    assert JEXL().evaluate(expression) == result


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[1, 2, 3]|min", 1),
        ("['a', 'b']|min", None),
        ("[1, 2, '3']|min", 1),
        ("['a', None]|min", None),
        ("[1, 2, 3]|max", 3),
        ("['a', 'b']|max", None),
        ("[1, 2, '3']|max", 2),
        ("['a', None]|max", None),
        ("[1, 2, 3]|sum", 6),
        ("['a', 'b']|sum", 0),
        ("[1, 2, '3']|sum", 3),
        ("['a', None]|sum", 0),
        ("1.2|ceil", 2),
        ("18.00001|ceil", 19),
        ("None|ceil", None),
        ("'a'|ceil", None),
        ("[1.2]|ceil", None),
        ("1.2|floor", 1),
        ("18.00001|floor", 18),
        ("None|floor", None),
        ("'a'|floor", None),
        ("[1.2]|floor", None),
        ("[1]|avg", 1),
        ("[2, 3]|avg", 2.5),
        ("[2, 3, None, 'foo']|avg", 2.5),
        ("[None, 'foo']|avg", None),
        ("1.49|round", 1),
        ("1.51|round", 2),
        ("1.49|round(1)", 1.5),
        ("1.49|round(2)", 1.49),
        ("1.4445|round(3)", 1.445),
        ("-0.5|round", 0),
        ("-1.14|round(1)", -1.1),
        ("-1.15|round(1)", -1.1),
        ("-1.16|round(1)", -1.2),
        ("'foo'|round", None),
        ("'foo'|round(1)", None),
        ("['foo']|round", None),
        ("['foo']|round(1)", None),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')", [1.4, 2.6]),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|min", 1.4),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|max", 2.6),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|min|round", 1),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|max|round", 3),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|max|round(1)", 2.6),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|sum", 4),
        ("[{ key: 1.4 }, {key: 2.6}]|mapby('key')|sum", 4),
        ("[[{ key: 1.4 }, {key: 2.6}]|mapby('key')|sum]|round", None),
    ],
)
def test_math_transforms(expression, result):
    assert JEXL().evaluate(expression) == result


@pytest.mark.parametrize(
    "expression,result",
    [
        ("[['test1', 'test2'], [1,2]]|stringify", '[["test1", "test2"], [1, 2]]'),
        ("1|stringify", "1"),
    ],
)
def test_stringify_transform(expression, result):
    assert JEXL().evaluate(expression) == result


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1 + 1", [1, 1]),
        ('["1", 2, 3]', ["1", 2, 3]),
        ('{key: ["foo", "bar"]}', ["foo", "bar"]),
        ("[1|round, [2, 3]|min]|avg", [1, 2, 3]),
    ],
)
def test_caluma_analyzer(expression, expected):
    class NodeAnalyzer(CalumaAnalyzer):
        def visit_Literal(self, node):
            yield node.value

    jexl = JEXL()
    assert list(jexl.analyze(expression, NodeAnalyzer)) == expected
