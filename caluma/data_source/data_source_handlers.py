from collections import namedtuple
from datetime import timedelta

from django.conf import settings
from django.utils.module_loading import import_string

from caluma.data_source.utils import cache_handler

DataSource = namedtuple("DataSource", ["name", "info"])


class DataSourceException(Exception):
    pass


def is_iterable_and_no_string(value):
    try:
        iter(value)
        return not isinstance(value, str)
    except TypeError:
        return False


class Data:
    def __init__(self, data):
        self.data = data
        self.option, self.value = self.load()

    def load(self):
        if is_iterable_and_no_string(self.data):
            if not 0 < len(self.data) < 3:
                raise DataSourceException(f"Failed to parse data:\n{self.data}")
            elif len(self.data) == 1:
                return str(self.data[0]), str(self.data[0])
            return str(self.data[0]), str(self.data[1])

        return str(self.data), str(self.data)


def get_data_sources(dic=False):
    """Get all configured DataSources.

    :param dic: Should return a dict
    :return: List of DataSource-objects if dic False otherwise dict
    """
    data_source_classes = [import_string(cls) for cls in settings.DATA_SOURCE_CLASSES]
    if dic:
        return {ds.__name__: ds for ds in data_source_classes}
    return [DataSource(name=ds.__name__, info=ds.info) for ds in data_source_classes]


def get_data_source_data(info, name):
    data_sources = get_data_sources(dic=True)
    if name not in data_sources:
        raise DataSourceException(f"No data_source found for name: {name}")
    cls = data_sources[name]
    ds = cls()
    key = f"data_source_{name}_{info.context.user.username}"
    raw_data = cache_handler(
        ds.get_data, timedelta(seconds=ds.timeout), ds.default, key, info=info
    )
    if not is_iterable_and_no_string(raw_data):
        raise DataSourceException(f"Failed to parse data from source: {name}")

    return [Data(d) for d in raw_data]
