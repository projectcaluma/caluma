from uuid import uuid4

from caluma.caluma_data_source.data_sources import BaseDataSource
from caluma.caluma_data_source.utils import data_source_cache


class MyDataSource(BaseDataSource):
    info = {"en": "Nice test data source", "de": "Schöne Datenquelle"}
    default = [1, 2, 3]

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        return [
            1,
            (5.5,),
            "sdkj",
            ("value", "info"),
            ["something"],
            [
                "translated_value",
                {"en": "english description", "de": "deutsche Beschreibung"},
            ],
        ]

    @data_source_cache(timeout=60)
    def get_data_test_string(self, info):
        return "test string"

    @data_source_cache(timeout=60)
    def get_data_uuid(self, info):
        return str(uuid4())

    @data_source_cache(timeout=1)
    def get_data_expire(self, info):
        return str(uuid4())


class MyOtherDataSource(MyDataSource):
    def validate_answer_value(self, value, document, question, info):
        return "Test 123"


class MyFaultyDataSource(BaseDataSource):
    info = "Faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        return "just a string"


class MyOtherFaultyDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        return [["just", "some", "strings"]]


class MyBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = [1, 2, 3]

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        raise Exception()


class MyOtherBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        raise Exception()
