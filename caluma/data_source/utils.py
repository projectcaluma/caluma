import logging

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


def cache_handler(func, timeout, default, key, *args, **kwargs):
    """
    Handle cache for data_sources.

    This function handles caching of the data from the data_sources.

    if cached data is not available
      - fetch the new data
        - if fetching new data succeeds
          - cache the new data and return it
        - if fetching new data fails
          - log an exception and return the default value
    if cached data is available
      - if timeout was hit
        - try to fetch new data
          - if fetching new data succeeds
            - cache the new data and return it
          - if fetching new data fails
            - log an exception and return the cached data
      - if timeout was not hit
        - return the cached data

    :param func: function for fetching new data. The function should raise an
                 exception on failure
    :param timeout: timeout for the cache
    :param default: default value to return if everything fails
    :param key: key for the cache
    :param args: additional args to be passed to func
    :param kwargs: additional kwargs to be passed to func
    :return: data
    """

    def get_new_data():
        new_data = func(*args, **kwargs)
        timestamp = timezone.now() + timeout
        cache.set(key, {"data": new_data, "valid_until": timestamp}, None)
        return new_data

    cached_data = cache.get(key, "not found in cache")
    if cached_data == "not found in cache":
        try:
            data = get_new_data()
        except Exception as e:
            logger.exception(
                f"Executing {func.__name__} failed: "
                f"{e}\n"
                f"Using default value: {default}"
            )
            return default
        return data
    else:
        if cached_data["valid_until"] > timezone.now():
            return cached_data["data"]
        else:
            try:
                data = get_new_data()
            except Exception as e:
                logger.exception(
                    f"Executing {func.__name__} failed:" f"{e}\n" f"Using cached data."
                )
                return cached_data["data"]
            return data
