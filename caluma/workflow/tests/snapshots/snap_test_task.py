# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_tasks 1"] = {
    "allTasks": {
        "edges": [
            {
                "node": {
                    "description": """First where during teach country talk across. Little central meeting anyone remember.
Material minute ago get. Range whose scientist draw free property consider. Have director true force.""",
                    "meta": "{}",
                    "name": "Jordan Mccarthy",
                    "slug": "mrs-shake-recent",
                    "type": "SIMPLE",
                }
            }
        ]
    }
}

snapshots["test_save_task 1"] = {
    "data": {
        "saveTask": {
            "clientMutationId": "testid",
            "task": {
                "meta": "{}",
                "name": "Jordan Mccarthy",
                "slug": "mrs-shake-recent",
                "type": "SIMPLE",
            },
        }
    },
    "errors": [],
}
