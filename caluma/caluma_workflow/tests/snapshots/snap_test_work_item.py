# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_complete_work_item_last[ready-completed-True-simple-None] 1"] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {"closedByUser": "admin", "status": "COMPLETED"},
            "closedByUser": "admin",
            "status": "COMPLETED",
        },
    }
}

snapshots["test_complete_multiple_instance_task_form_work_item_next[integer-1] 1"] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["group-name"],
                                "status": "READY",
                            }
                        },
                        {"node": {"addressedGroups": [], "status": "COMPLETED"}},
                        {"node": {"addressedGroups": [], "status": "COMPLETED"}},
                    ],
                    "totalCount": 3,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots["test_complete_work_item_with_next[ready-None-simple] 1"] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["group-name"],
                                "status": "READY",
                            }
                        },
                        {"node": {"addressedGroups": [], "status": "COMPLETED"}},
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}
