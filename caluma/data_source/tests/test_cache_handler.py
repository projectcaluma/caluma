from datetime import timedelta
from time import sleep

from django.core.cache import cache

from caluma.data_source.utils import cache_handler


def my_func(my_arg):
    return my_arg


def my_broken_func():
    return 7 / 0


def test_set_cache():
    cache.clear()
    result = cache_handler(
        my_func, timedelta(seconds=10), None, "test_cache_key", "test string"
    )
    assert result == "test string"
    assert cache.get("test_cache_key")["data"] == "test string"


def test_get_from_cache():
    cache.clear()
    cache_handler(my_func, timedelta(seconds=10), None, "test_cache_key", "test string")
    cached_result1 = cache.get("test_cache_key")
    cache_handler(my_func, timedelta(seconds=10), None, "test_cache_key", "test string")
    cached_result2 = cache.get("test_cache_key")
    assert cached_result1 == cached_result2


def test_expired_cache():
    cache.clear()
    cache_handler(my_func, timedelta(seconds=1), None, "test_cache_key", "test string")
    cached_result1 = cache.get("test_cache_key")
    sleep(1.1)
    cache_handler(my_func, timedelta(seconds=1), None, "test_cache_key", "test string")
    cached_result2 = cache.get("test_cache_key")
    assert not cached_result1 == cached_result2


def test_default_value():
    cache.clear()
    result = cache_handler(
        my_broken_func, timedelta(seconds=10), "default", "test_cache_key"
    )
    assert result == "default"
    cache_handler(
        my_func, timedelta(seconds=1), "default", "test_cache_key", "test string"
    )
    sleep(1.1)
    result = cache_handler(
        my_broken_func, timedelta(seconds=10), "default", "test_cache_key"
    )
    assert result == "test string"
