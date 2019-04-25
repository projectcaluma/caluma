from caluma.data_source.data_sources import BaseDataSource


class MyDataSource(BaseDataSource):
    info = "Nice test data source"
    timeout = 3600
    default = []

    def get_data(self, info):
        return [1, 5.5, "sdkj", ["info", "value"], ["something"]]


class MyFaultyDataSource(BaseDataSource):
    info = "Nice test data source"
    timeout = 3600
    default = []

    def get_data(self, info):
        return "just a string"


class MyOtherFaultyDataSource(BaseDataSource):
    info = "Nice test data source"
    timeout = 3600
    default = []

    def get_data(self, info):
        return [["just", "some", "strings"]]
