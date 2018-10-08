# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_workflows 1"] = {
    "allWorkflows": {"edges": [{"node": {"status": "RUNNING"}}]}
}

snapshots["test_start_workflow 1"] = {
    "startWorkflow": {
        "clientMutationId": None,
        "workflow": {
            "form": {"formSpecification": {"slug": "star-check-record"}},
            "status": "RUNNING",
            "tasks": {"edges": [{"node": {"status": "READY"}}]},
        },
    }
}
