# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_query_all_workflows 1"] = {
    "allWorkflows": {
        "edges": [
            {
                "node": {
                    "allowAllForms": False,
                    "allowForms": {"edges": [{"node": {"slug": "sound-air-mission"}}]},
                    "description": """Line whatever team suggest traditional boy. Drop argue move. Anyone remember prove.
Kid avoid player relationship to range whose. Draw free property consider.""",
                    "flows": {
                        "edges": [
                            {
                                "node": {
                                    "next": "mrs-positive",
                                    "tasks": [{"slug": "few-list-tax"}],
                                }
                            }
                        ],
                        "totalCount": 1,
                    },
                    "meta": {},
                    "name": "Brian Williams",
                    "slug": "effort-meet",
                    "startTasks": [{"slug": "few-list-tax"}],
                    "tasks": [{"slug": "few-list-tax"}],
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_save_workflow 1"] = {
    "saveWorkflow": {
        "clientMutationId": "testid",
        "workflow": {
            "allowAllForms": False,
            "allowForms": {
                "edges": [{"node": {"slug": "sound-air-mission"}}],
                "totalCount": 1,
            },
            "meta": {},
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}

snapshots['test_add_workflow_flow[task-slug-"task-slug"|task-True] 1'] = {
    "addWorkflowFlow": {
        "clientMutationId": None,
        "workflow": {
            "flows": {
                "edges": [
                    {
                        "node": {
                            "createdByGroup": "admin",
                            "createdByUser": "admin",
                            "next": '"task-slug"|task',
                            "tasks": [{"slug": "task-slug"}],
                        }
                    }
                ],
                "totalCount": 1,
            },
            "tasks": [
                {"slug": "task-slug"},
                {"slug": "service-bank-arm"},
                {"slug": "relate-right-will"},
            ],
        },
    }
}
