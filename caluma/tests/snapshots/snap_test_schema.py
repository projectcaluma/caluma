# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_schema_queries[queries/AllFormsQuery.graphql] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "description": "Bit among again across environment long line. Team suggest traditional boy above.",
                    "id": "Rm9ybTptcnMtc2hha2UtcmVjZW50",
                    "meta": "{}",
                    "name": "Jordan Mccarthy",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "UXVlc3Rpb246cmF0aGVyLWNvc3QtYWRtaXQ=",
                                    "label": "Courtney Brewer",
                                    "slug": "rather-cost-admit",
                                }
                            }
                        ]
                    },
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}

snapshots["test_schema_queries[queries/AllQuestionsQuery.graphql] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "configuration": "{}",
                    "id": "UXVlc3Rpb246cmF0aGVyLWNvc3QtYWRtaXQ=",
                    "label": "Courtney Brewer",
                    "meta": "{}",
                    "slug": "rather-cost-admit",
                    "type": "INTEGER",
                }
            }
        ]
    }
}
