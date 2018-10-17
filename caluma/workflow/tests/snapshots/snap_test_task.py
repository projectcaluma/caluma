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
                    "description": "Team suggest traditional boy above. Argue move appear catch toward help wind. Material minute ago get.",
                    "meta": "{}",
                    "name": "Brian Williams",
                    "slug": "effort-meet",
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
                "name": "Brian Williams",
                "slug": "effort-meet",
                "type": "SIMPLE",
            },
        }
    },
    "errors": [],
}
