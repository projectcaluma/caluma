from uuid import uuid4

from caluma.caluma_data_source.data_sources import BaseDataSource
from caluma.caluma_data_source.utils import data_source_cache


class MyDataSource(BaseDataSource):
    info = {"en": "Nice test data source", "de": "Schöne Datenquelle"}
    default = [1, 2, 3]

    @data_source_cache(timeout=3600)
    def get_data(self, user, question, context):
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
    def validate_answer_value(self, value, document, question, info, context):
        return "Test 123"


class MyFaultyDataSource(BaseDataSource):
    info = "Faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, user, question, context):
        return "just a string"


class MyOtherFaultyDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, user, question, context):
        return [["just", "some", "strings"]]


class MyBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = [1, 2, 3]

    @data_source_cache(timeout=3600)
    def get_data(self, user, question, context):
        raise Exception()


class MyOtherBrokenDataSource(BaseDataSource):
    info = "Other faulty test data source"
    default = None

    @data_source_cache(timeout=3600)
    def get_data(self, user, question, context):
        raise Exception()


class MyDataSourceWithContext(BaseDataSource):
    info = "Data source using context for testing"

    def get_data(self, user, question, context):
        if not question:
            return []

        slug = "option-without-context"
        label = f"q: {question.slug}"

        if context:
            slug = "option-with-context"
            label += f" foo: {context['foo']}"

        return [[slug, label]]
