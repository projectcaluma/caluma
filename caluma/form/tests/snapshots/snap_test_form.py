# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_form 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTptcnMtc2hha2UtcmVjZW50",
            "meta": "{}",
            "name": "Jordan Mccarthy",
            "slug": "mrs-shake-recent",
        },
    }
}

snapshots["test_query_all_forms 1"] = {
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

snapshots["test_add_form_question 1"] = {
    "data": {
        "addFormQuestion": {
            "clientMutationId": None,
            "form": {"questions": {"edges": [{"node": {"slug": "fly-even-yourself"}}]}},
        }
    },
    "errors": [],
}

snapshots["test_remove_form_question 1"] = {
    "data": {
        "removeFormQuestion": {
            "clientMutationId": None,
            "form": {"questions": {"edges": []}},
        }
    },
    "errors": [],
}
