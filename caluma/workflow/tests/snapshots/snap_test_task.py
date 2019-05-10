# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_query_all_tasks[simple] 1"] = {
    "allTasks": {
        "edges": [
            {
                "node": {
                    "__typename": "SimpleTask",
                    "description": "State section rock event recent. Final activity hope star check record well. Radio with Mr letter eye.",
                    "meta": {},
                    "name": "Thomas Johnson",
                    "slug": "sound-air-mission",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_save_task[SaveSimpleTask] 1"] = {
    "saveSimpleTask": {
        "clientMutationId": "testid",
        "task": {
            "__typename": "SimpleTask",
            "meta": {},
            "name": "Thomas Johnson",
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_task[SaveCompleteWorkflowFormTask] 1"] = {
    "saveCompleteWorkflowFormTask": {
        "clientMutationId": "testid",
        "task": {
            "__typename": "CompleteWorkflowFormTask",
            "meta": {},
            "name": "Thomas Johnson",
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_comlete_task_form_task 1"] = {
    "saveCompleteTaskFormTask": {
        "clientMutationId": "testid",
        "task": {
            "__typename": "CompleteTaskFormTask",
            "meta": {},
            "name": "Thomas Johnson",
            "slug": "sound-air-mission",
        },
    }
}
