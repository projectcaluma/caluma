import pytest

from ..collections import list_duplicates


@pytest.mark.parametrize("iterator,expected", [([1, 2, 3], set()), ([1, 1, 2, 3], {1})])
def test_list_duplicates(iterator, expected):
    assert list_duplicates(iterator) == expected
