# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_start_case[startCase-["group-name"]|groups-100] 1'] = {
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

snapshots['test_start_case[startCase-["group-name"]|groups-None] 1'] = {
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

snapshots["test_start_case[startCase-None-100] 1"] = {
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

snapshots["test_start_case[startCase-None-None] 1"] = {
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

snapshots['test_start_case[saveCase-["group-name"]|groups-100] 1'] = {
    "saveCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": {"status": "READY"},
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

snapshots['test_start_case[saveCase-["group-name"]|groups-None] 1'] = {
    "saveCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": {"status": "READY"},
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

snapshots["test_start_case[saveCase-None-100] 1"] = {
    "saveCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": {"status": "READY"},
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

snapshots["test_start_case[saveCase-None-None] 1"] = {
    "saveCase": {
        "case": {
            "document": {"form": {"slug": "sound-air-mission"}},
            "parentWorkItem": {"status": "READY"},
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

snapshots["test_query_all_cases[running-1] 1"] = {
    "allCases": {"edges": [{"node": {"status": "RUNNING"}}]}
}

snapshots["test_query_all_cases[completed-0] 1"] = {"allCases": {"edges": []}}

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
