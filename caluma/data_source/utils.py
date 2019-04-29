import functools
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


def data_source_cache(timeout=None):
    def decorator(method):
        @functools.wraps(method)
        def handle_cache(self, info):
            key = f"data_source_{type(self).__name__}"

            get_data_method = functools.partial(method, self, info)
            return cache.get_or_set(key, get_data_method, timeout)

        return handle_cache

    return decorator
