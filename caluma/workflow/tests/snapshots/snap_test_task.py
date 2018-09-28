# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_tasks 1"] = {
    "allTasks": {"edges": [{"node": {"status": "COMPLETE"}}]}
}

snapshots["test_complete_task_last[ready-True] 1"] = {
    "completeTask": {
        "clientMutationId": None,
        "task": {"status": "COMPLETE", "workflow": {"status": "COMPLETE"}},
    }
}

snapshots["test_complete_task_with_next[ready] 1"] = {
    "completeTask": {
        "clientMutationId": None,
        "task": {
            "status": "COMPLETE",
            "workflow": {
                "status": "COMPLETE",
                "tasks": {
                    "edges": [
                        {"node": {"status": "READY"}},
                        {"node": {"status": "COMPLETE"}},
                    ]
                },
            },
        },
    }
}
