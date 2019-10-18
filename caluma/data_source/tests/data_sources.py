from uuid import uuid4

from caluma.data_source.data_sources import BaseDataSource
from caluma.data_source.utils import data_source_cache


class MyDataSource(BaseDataSource):
    info = {"en": "Nice test data source", "de": "Schöne Datenquelle"}
    default = [1, 2, 3]
    validate = True

    @data_source_cache(timeout=3600)
    def get_data(self, info, answer_value=None):
        return [
            1,
            5.5,
            "sdkj",
            ["value", "info"],
            ["something"],
            [
                "translated_value",
                {"en": "english description", "de": "deutsche Beschreibung"},
            ],
        ]

    @data_source_cache(timeout=60)
    def get_data_test_string(self, info, answer_value=None):
        return "test string"

    @data_source_cache(timeout=60)
    def get_data_uuid(self, info, answer_value=None):
        return str(uuid4())

    @data_source_cache(timeout=1)
    def get_data_expire(self, info, answer_value=None):
        return str(uuid4())


class MyOtherDataSource(MyDataSource):
    validate = False


class MyFaultyDataSource(BaseDataSource):
    info = "Faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info, answer_value=None):
        return "just a string"


class MyOtherFaultyDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info, answer_value=None):
        return [["just", "some", "strings"]]


class MyBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = [1, 2, 3]

    @data_source_cache(timeout=3600)
    def get_data(self, info, answer_value=None):
        raise Exception()


class MyOtherBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info, answer_value=None):
        raise Exception()
