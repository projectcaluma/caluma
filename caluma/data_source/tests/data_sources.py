from caluma.data_source.data_sources import BaseDataSource


class MyDataSource(BaseDataSource):
    info = {"en": "Nice test data source", "de": "Schöne Datenquelle"}
    timeout = 3600
    default = []

    def get_data(self, info):
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


class MyFaultyDataSource(BaseDataSource):
    info = "Faulty test data source"
    timeout = 3600
    default = []

    def get_data(self, info):
        return "just a string"


class MyOtherFaultyDataSource(BaseDataSource):
    info = "Other faulty test data source"
    timeout = 3600
    default = []

    def get_data(self, info):
        return [["just", "some", "strings"]]
