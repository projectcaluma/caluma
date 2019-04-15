# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_fetch_data_sources 1"] = {
    "allDataSources": {
        "edges": [{"node": {"info": "Nice test data source", "name": "MyDataSource"}}],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjA=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
    }
}

snapshots["test_fetch_data_from_data_source 1"] = {
    "dataSource": {
        "edges": [
            {"node": {"option": "1", "value": "1"}},
            {"node": {"option": "5.5", "value": "5.5"}},
            {"node": {"option": "sdkj", "value": "sdkj"}},
            {"node": {"option": "info", "value": "value"}},
            {"node": {"option": "something", "value": "something"}},
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjQ=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
    }
}
