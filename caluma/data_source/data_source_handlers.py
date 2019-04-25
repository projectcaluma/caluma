from collections import namedtuple
from datetime import timedelta

from caluma.data_source.utils import cache_handler
from caluma.extensions import data_sources

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


def get_data_sources():
    sources = []
    for name in dir(data_sources):
        cls = getattr(data_sources, name)
        if (
            isinstance(cls, type)
            and name.endswith("DataSource")
            and not name == "BaseDataSource"
        ):
            sources.append(DataSource(name=name, info=cls.info))
    return sources


def get_data_source_data(info, name):
    try:
        cls = getattr(data_sources, name)
    except AttributeError:
        raise DataSourceException(f"No data_source found for name: {name}")
    ds = cls()
    key = f"data_source_{name}_{info.context.user.username}"
    raw_data = cache_handler(
        ds.get_data, timedelta(seconds=ds.timeout), ds.default, key, info=info
    )
    if not is_iterable_and_no_string(raw_data):
        raise DataSourceException(f"Failed to parse data from source: {name}")

    return [Data(d) for d in raw_data]
