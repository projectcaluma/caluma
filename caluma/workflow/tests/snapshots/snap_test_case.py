# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_cases 1"] = {
    "allCases": {"edges": [{"node": {"status": "RUNNING"}}]}
}

snapshots["test_cancel_case[running-True-completed] 1"] = {
    "cancelCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "status": "CANCELED",
            "workItems": {"edges": [{"node": {"status": "COMPLETED"}}]},
        },
        "clientMutationId": None,
    }
}

snapshots["test_cancel_case[running-True-ready] 1"] = {
    "cancelCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "status": "CANCELED",
            "workItems": {"edges": [{"node": {"status": "CANCELED"}}]},
        },
        "clientMutationId": None,
    }
}

snapshots['test_start_case[["group-name"]|groups-100] 1'] = {
    "startCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": None,
            "status": "RUNNING",
            "workItems": {
                "edges": [
                    {
                        "node": {
                            "addressedGroups": ["group-name"],
                            "document": {"form": {"slug": "sound-air-mission"}},
                            "status": "READY",
                        }
                    }
                ]
            },
        },
        "clientMutationId": None,
    }
}

snapshots['test_start_case[["group-name"]|groups-None] 1'] = {
    "startCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": None,
            "status": "RUNNING",
            "workItems": {
                "edges": [
                    {
                        "node": {
                            "addressedGroups": ["group-name"],
                            "document": {"form": {"slug": "sound-air-mission"}},
                            "status": "READY",
                        }
                    }
                ]
            },
        },
        "clientMutationId": None,
    }
}

snapshots["test_start_case[None-100] 1"] = {
    "startCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": None,
            "status": "RUNNING",
            "workItems": {
                "edges": [
                    {
                        "node": {
                            "addressedGroups": [],
                            "document": {"form": {"slug": "sound-air-mission"}},
                            "status": "READY",
                        }
                    }
                ]
            },
        },
        "clientMutationId": None,
    }
}

snapshots["test_start_case[None-None] 1"] = {
    "startCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": None,
            "status": "RUNNING",
            "workItems": {
                "edges": [
                    {
                        "node": {
                            "addressedGroups": [],
                            "document": {"form": {"slug": "sound-air-mission"}},
                            "status": "READY",
                        }
                    }
                ]
            },
        },
        "clientMutationId": None,
    }
}
