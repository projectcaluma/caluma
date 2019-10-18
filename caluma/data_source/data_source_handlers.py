from collections import namedtuple

from django.conf import settings
from django.utils.module_loading import import_string

from caluma.core.utils import translate_value

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
        self.slug, self.label = self.load()

    def load(self):
        if is_iterable_and_no_string(self.data):
            if not 0 < len(self.data) < 3:
                raise DataSourceException(f"Failed to parse data:\n{self.data}")
            elif len(self.data) == 1:
                return str(self.data[0]), str(self.data[0])
            elif isinstance(self.data[1], dict):
                return (
                    str(self.data[0]),
                    str(translate_value(self.data[1]) or self.data[0]),
                )
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
    return [
        DataSource(name=ds.__name__, info=translate_value(ds.info))
        for ds in data_source_classes
    ]


def get_data_source_data(info, name, answer_value=None):
    data_sources = get_data_sources(dic=True)
    if name not in data_sources:
        raise DataSourceException(f"No data_source found for name: {name}")

    raw_data = data_sources[name]().try_get_data_with_fallback(info, answer_value)
    if not is_iterable_and_no_string(raw_data):
        raise DataSourceException(f"Failed to parse data from source: {name}")

    return [Data(d) for d in raw_data]
