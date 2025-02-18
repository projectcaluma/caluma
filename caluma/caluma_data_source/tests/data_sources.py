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


class MyDataSourceWithOnCopy(BaseDataSource):
    info = "Data source using on copy for testing"

    def get_data(self):
        return [
            ["169cac4c-ab46-4521-bdba-4385f26ffb3", "label1"],
            ["34948dc6-4b16-4a72-890b-cdbdc7da9f2", "label2"],
            ["0935c1bc-5ff3-44a4-9089-03eac8872b0", "label3"],
        ]

    def get_change_value(self):
        return ["changedv-4b16-4a72-890b-cdbdc7da9f2", "changed label2"]

    def on_copy(self, old_answer, new_answer, old_value):
        old_slug, _ = old_value

        if old_slug == "discard":
            return (None, None)

        if old_slug == "change":
            return self.get_change_value()

        return old_value
