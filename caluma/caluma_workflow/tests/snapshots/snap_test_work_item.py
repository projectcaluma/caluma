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

snapshots[
    'test_complete_work_item_with_next[["some-group"]|groups-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1'
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["some-group"],
                                "controllingGroups": ["some-group"],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[prev_work_item_controlling_groups-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[work_item_creating_group-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["fake-user-group"],
                                "controllingGroups": ["fake-user-group"],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[case_creating_group-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["case-creating-group"],
                                "controllingGroups": ["case-creating-group"],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[[case_creating_group, work_item_creating_group]|groups-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "controllingGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[info.prev_work_item.controlling_groups-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[info.work_item.created_by_group-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["fake-user-group"],
                                "controllingGroups": ["fake-user-group"],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[info.case.created_by_group-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": ["case-creating-group"],
                                "controllingGroups": ["case-creating-group"],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[[info.case.created_by_group, info.work_item.created_by_group]|groups-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "controllingGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}

snapshots[
    "test_complete_work_item_with_next[[info.case.created_by_group, info.work_item.created_by_group]-ready-None-simple-work_item__controlling_groups0-work-item-creating-group-case-creating-group] 1"
] = {
    "completeWorkItem": {
        "clientMutationId": None,
        "workItem": {
            "case": {
                "status": "RUNNING",
                "workItems": {
                    "edges": [
                        {
                            "node": {
                                "addressedGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "controllingGroups": [
                                    "case-creating-group",
                                    "fake-user-group",
                                ],
                                "status": "READY",
                            }
                        },
                        {
                            "node": {
                                "addressedGroups": [],
                                "controllingGroups": [
                                    "controlling-group1",
                                    "controlling-group2",
                                ],
                                "status": "COMPLETED",
                            }
                        },
                    ],
                    "totalCount": 2,
                },
            },
            "status": "COMPLETED",
        },
    }
}
