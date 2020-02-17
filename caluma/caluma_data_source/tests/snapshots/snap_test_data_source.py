# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_fetch_data_sources 1"] = {
    "allDataSources": {
        "edges": [
            {"node": {"info": "Nice test data source", "name": "MyDataSource"}},
            {"node": {"info": "Faulty test data source", "name": "MyFaultyDataSource"}},
            {
                "node": {
                    "info": "Other faulty test data source",
                    "name": "MyOtherFaultyDataSource",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_data_sources 2"] = {
    "allDataSources": {
        "edges": [
            {"node": {"info": "Schöne Datenquelle", "name": "MyDataSource"}},
            {"node": {"info": "Faulty test data source", "name": "MyFaultyDataSource"}},
            {
                "node": {
                    "info": "Other faulty test data source",
                    "name": "MyOtherFaultyDataSource",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_data_sources 3"] = {
    "allDataSources": {
        "edges": [
            {"node": {"info": "Nice test data source", "name": "MyDataSource"}},
            {"node": {"info": "Faulty test data source", "name": "MyFaultyDataSource"}},
            {
                "node": {
                    "info": "Other faulty test data source",
                    "name": "MyOtherFaultyDataSource",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_data_from_data_source 1"] = {
    "dataSource": {
        "edges": [
            {"node": {"label": "1", "slug": "1"}},
            {"node": {"label": "5.5", "slug": "5.5"}},
            {"node": {"label": "sdkj", "slug": "sdkj"}},
            {"node": {"label": "info", "slug": "value"}},
            {"node": {"label": "something", "slug": "something"}},
            {"node": {"label": "english description", "slug": "translated_value"}},
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjU=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 6,
    }
}

snapshots["test_data_source_defaults 1"] = {
    "dataSource": {
        "edges": [
            {"node": {"label": "1", "slug": "1"}},
            {"node": {"label": "2", "slug": "2"}},
            {"node": {"label": "3", "slug": "3"}},
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_data_from_data_source 2"] = {
    "dataSource": {
        "edges": [
            {"node": {"label": "1", "slug": "1"}},
            {"node": {"label": "5.5", "slug": "5.5"}},
            {"node": {"label": "sdkj", "slug": "sdkj"}},
            {"node": {"label": "info", "slug": "value"}},
            {"node": {"label": "something", "slug": "something"}},
            {"node": {"label": "deutsche Beschreibung", "slug": "translated_value"}},
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjU=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 6,
    }
}

snapshots["test_fetch_data_from_data_source 3"] = {
    "dataSource": {
        "edges": [
            {"node": {"label": "1", "slug": "1"}},
            {"node": {"label": "5.5", "slug": "5.5"}},
            {"node": {"label": "sdkj", "slug": "sdkj"}},
            {"node": {"label": "info", "slug": "value"}},
            {"node": {"label": "something", "slug": "something"}},
            {"node": {"label": "english description", "slug": "translated_value"}},
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjU=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 6,
    }
}
