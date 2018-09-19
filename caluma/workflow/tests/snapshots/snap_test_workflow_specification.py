# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_workflow_specifications 1"] = {
    "allWorkflowSpecifications": {
        "edges": [
            {
                "node": {
                    "description": "Street hair local kind debate. Half long will third treat better note. Risk tonight miss south speak. Since region participant report us computer.",
                    "flows": {
                        "edges": [
                            {
                                "node": {
                                    "next": "value-still-back",
                                    "taskSpecification": {"slug": "mrs-shake-recent"},
                                }
                            }
                        ]
                    },
                    "meta": "{}",
                    "name": "Melanie Madden",
                    "slug": "star-check-record",
                }
            }
        ]
    }
}

snapshots["test_save_workflow_specification 1"] = {
    "saveWorkflowSpecification": {
        "clientMutationId": "testid",
        "workflowSpecification": {
            "meta": "{}",
            "name": "Melanie Madden",
            "slug": "star-check-record",
        },
    }
}

snapshots[
    'test_publish_workflow_specification[task-slug-"task-slug"|taskSpecification] 1'
] = {
    "data": {
        "publishWorkflowSpecification": {
            "clientMutationId": "testid",
            "workflowSpecification": {"isPublished": True},
        }
    },
    "errors": [],
}

snapshots[
    'test_publish_workflow_specification[task-slug-"not-av-task-slug"|taskSpecification] 1'
] = {
    "data": {"publishWorkflowSpecification": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'non_field_errors': [ErrorDetail(string='Task specifications `not-av-task-slug` specified in expression `\"not-av-task-slug\"|taskSpecification` but only `task-slug` are available in workflow specification `deep-public-these`', code='invalid')]}",
            "path": ["publishWorkflowSpecification"],
        }
    ],
}

snapshots["test_add_workflow_specification_flow[task-slug|taskSpecification] 1"] = {
    "data": {
        "addWorkflowSpecificationFlow": {
            "clientMutationId": None,
            "workflowSpecification": {
                "flows": {
                    "edges": [
                        {
                            "node": {
                                "next": "task-slug|taskSpecification",
                                "taskSpecification": {"slug": "mrs-shake-recent"},
                            }
                        }
                    ]
                }
            },
        }
    },
    "errors": [],
}

snapshots["test_add_workflow_specification_flow[task-slug|invalid] 1"] = {
    "data": {"addWorkflowSpecificationFlow": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'next': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["addWorkflowSpecificationFlow"],
        }
    ],
}
