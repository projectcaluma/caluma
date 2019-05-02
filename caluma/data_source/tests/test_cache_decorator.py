from time import sleep

from django.core.cache import cache

from .data_sources import MyDataSource


def test_set_cache(info):
    cache.clear()
    ds = MyDataSource()
    result = ds.get_data_test_string(info)
    assert result == "test string"
    assert cache.get("data_source_MyDataSource") == "test string"


def test_get_from_cache(info):
    cache.clear()
    ds = MyDataSource()
    ds.get_data_uuid(info)
    cached_result = cache.get("data_source_MyDataSource")
    new_result = ds.get_data_uuid(info)
    assert cached_result == new_result


def test_expired_cache(info):
    cache.clear()
    ds = MyDataSource()
    ds.get_data_expire(info)
    cached_result = cache.get("data_source_MyDataSource")

    sleep(1.1)
    new_result = ds.get_data_uuid(info)

    assert not cached_result == new_result
