# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_cases[running-1] 1"] = {
    "allCases": {"edges": [{"node": {"status": "RUNNING"}}], "totalCount": 1}
}

snapshots["test_query_all_cases[completed-0] 1"] = {
    "allCases": {"edges": [], "totalCount": 0}
}

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

snapshots["test_order_by_question_answer_value[text-True-True] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "a"}},
                                {"node": {"stringValue": "b2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "b"}},
                                {"node": {"stringValue": "c2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "c"}},
                                {"node": {"stringValue": "a2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[text-True-False] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "c"}},
                                {"node": {"stringValue": "a2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "b"}},
                                {"node": {"stringValue": "c2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"stringValue": "a"}},
                                {"node": {"stringValue": "b2"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[form-True-True] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "b"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "d"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "f"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[form-True-False] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "f"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "d"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [{"node": {"stringValue": "b"}}],
                            "totalCount": 1,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[date-True-True] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-27"}},
                                {"node": {"dateValue": "2019-05-28"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-29"}},
                                {"node": {"dateValue": "2019-05-30"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-31"}},
                                {"node": {"dateValue": "2019-05-26"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[date-True-False] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-31"}},
                                {"node": {"dateValue": "2019-05-26"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-29"}},
                                {"node": {"dateValue": "2019-05-30"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"dateValue": "2019-05-27"}},
                                {"node": {"dateValue": "2019-05-28"}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[file-True-True] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "b"}}},
                                {"node": {"fileValue": {"name": "e"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "d"}}},
                                {"node": {"fileValue": {"name": "c"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "f"}}},
                                {"node": {"fileValue": {"name": "a"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}

snapshots["test_order_by_question_answer_value[file-True-False] 1"] = {
    "allCases": {
        "edges": [
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "f"}}},
                                {"node": {"fileValue": {"name": "a"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "d"}}},
                                {"node": {"fileValue": {"name": "c"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
            {
                "node": {
                    "document": {
                        "answers": {
                            "edges": [
                                {"node": {"fileValue": {"name": "b"}}},
                                {"node": {"fileValue": {"name": "e"}}},
                            ],
                            "totalCount": 2,
                        }
                    }
                }
            },
        ],
        "totalCount": 3,
    }
}
