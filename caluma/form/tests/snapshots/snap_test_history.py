# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_document_as_of 1"] = {
    "documentAsOf": {
        "answers": {
            "edges": [
                {
                    "node": {
                        "__typename": "HistoricalStringAnswer",
                        "historyUserId": "admin",
                        "value": "first admin - revision 1",
                    }
                }
            ]
        },
        "meta": {},
    }
}

snapshots["test_document_as_of 2"] = {
    "documentAsOf": {
        "answers": {
            "edges": [
                {
                    "node": {
                        "__typename": "HistoricalStringAnswer",
                        "historyUserId": "AnonymousUser",
                        "value": "first anon - revision 3",
                    }
                }
            ]
        },
        "meta": {},
    }
}

snapshots["test_document_as_of 3"] = {
    "documentAsOf": {
        "answers": {
            "edges": [
                {
                    "node": {
                        "__typename": "HistoricalStringAnswer",
                        "historyUserId": "AnonymousUser",
                        "value": "second anon - revision 4",
                    }
                }
            ]
        },
        "meta": {},
    }
}

snapshots["test_historical_table_answer 1"] = {
    "documentAsOf": {
        "answers": {
            "edges": [
                {
                    "node": {
                        "__typename": "HistoricalTableAnswer",
                        "value": [
                            {
                                "answers": {
                                    "edges": [{"node": {"value": "first row value"}}]
                                }
                            },
                            {
                                "answers": {
                                    "edges": [{"node": {"value": "second row value"}}]
                                }
                            },
                        ],
                    }
                }
            ]
        }
    }
}

snapshots["test_historical_table_answer 2"] = {
    "documentAsOf": {
        "answers": {
            "edges": [
                {
                    "node": {
                        "__typename": "HistoricalTableAnswer",
                        "value": [
                            {
                                "answers": {
                                    "edges": [{"node": {"value": "first row value"}}]
                                }
                            }
                        ],
                    }
                }
            ]
        }
    }
}
