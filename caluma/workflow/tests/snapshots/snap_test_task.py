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
                    "__typename": "SimpleTask",
                    "description": "Team suggest traditional boy above. Argue move appear catch toward help wind. Material minute ago get.",
                    "meta": "{}",
                    "name": "Brian Williams",
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_save_task[SaveSimpleTask] 1"] = {
    "data": {
        "saveSimpleTask": {
            "clientMutationId": "testid",
            "task": {
                "__typename": "SimpleTask",
                "meta": "{}",
                "name": "Brian Williams",
                "slug": "effort-meet",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_task[SaveCompleteWorkflowFormTask] 1"] = {
    "data": {
        "saveCompleteWorkflowFormTask": {
            "clientMutationId": "testid",
            "task": {
                "__typename": "SimpleTask",
                "meta": "{}",
                "name": "Brian Williams",
                "slug": "effort-meet",
            },
        }
    },
    "errors": [],
}
