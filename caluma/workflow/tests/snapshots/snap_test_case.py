# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_cases 1"] = {
    "allCases": {"edges": [{"node": {"status": "RUNNING"}}]}
}

snapshots["test_start_case 1"] = {
    "startCase": {
        "case": {
            "document": {"form": {"slug": "star-check-record"}},
            "status": "RUNNING",
            "workItems": {"edges": [{"node": {"status": "READY"}}]},
        },
        "clientMutationId": None,
    }
}
