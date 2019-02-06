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
                    "allowForms": {"edges": [{"node": {"slug": "effort-meet"}}]},
                    "description": """Role include money center of yes. Land subject another government animal pressure. Game respond mouth despite culture be magazine.
Hot morning future throughout guess language drive.""",
                    "flows": {
                        "edges": [
                            {
                                "node": {
                                    "next": "mrs-positive",
                                    "tasks": [{"slug": "sound-air-mission"}],
                                }
                            }
                        ]
                    },
                    "meta": "{}",
                    "name": "Renee Ayala",
                    "slug": "few-list-tax",
                }
            }
        ]
    }
}

snapshots["test_save_workflow 1"] = {
    "saveWorkflow": {
        "clientMutationId": "testid",
        "workflow": {
            "allowAllForms": False,
            "allowForms": {"edges": [{"node": {"slug": "effort-meet"}}]},
            "meta": "{}",
            "name": "Renee Ayala",
            "slug": "few-list-tax",
        },
    }
}

snapshots['test_add_workflow_flow[task-slug-"task-slug"|task] 1'] = {
    "data": {
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
                    ]
                }
            },
        }
    },
    "errors": [],
}

snapshots['test_add_workflow_flow[task-slug-"not-av-task-slug"|task] 1'] = {
    "data": {"addWorkflowFlow": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'next': [ErrorDetail(string='jexl `\"not-av-task-slug\"|task` contains invalid tasks [not-av-task-slug]', code='invalid')]}",
            "path": ["addWorkflowFlow"],
        }
    ],
}

snapshots['test_add_workflow_flow[task-slug-"not-av-task-slug"|invalid] 1'] = {
    "data": {"addWorkflowFlow": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'next': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["addWorkflowFlow"],
        }
    ],
}

snapshots['test_add_workflow_flow[task-slug-""] 1'] = {
    "data": {"addWorkflowFlow": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'next': [ErrorDetail(string='jexl `\"\"` does not contain any tasks as return value', code='invalid')]}",
            "path": ["addWorkflowFlow"],
        }
    ],
}
