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
                    "description": """Story first where during teach.
Across drop argue move. Anyone remember prove.
Kid avoid player relationship to range whose. Draw free property consider.""",
                    "id": "Rm9ybTptcnMtc2hha2UtcmVjZW50",
                    "meta": "{}",
                    "name": "Jordan Mccarthy",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "UXVlc3Rpb246Zmx5LWV2ZW4teW91cnNlbGY=",
                                    "label": "Amanda Boyd",
                                    "slug": "fly-even-yourself",
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
                    "id": "UXVlc3Rpb246Zmx5LWV2ZW4teW91cnNlbGY=",
                    "label": "Amanda Boyd",
                    "meta": "{}",
                    "slug": "fly-even-yourself",
                    "type": "RADIO",
                }
            }
        ]
    }
}
