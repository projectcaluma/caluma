# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_work_items 1"] = {
    "allWorkItems": {"edges": [{"node": {"status": "READY"}}]}
}

snapshots["test_complete_work_item_last[ready-True] 1"] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {"case": {"status": "COMPLETED"}, "status": "COMPLETED"},
    }
}

snapshots["test_complete_work_item_with_next[ready] 1"] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {"node": {"status": "READY"}},
                        {"node": {"status": "COMPLETED"}},
                    ]
                },
            },
            "status": "COMPLETED",
        },
    }
}
