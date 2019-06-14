# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_query_all_forms[First result-1st-float] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "description": "First result",
                    "id": "Rm9ybTplZmZvcnQtbWVldA==",
                    "meta": {},
                    "name": "1st",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "RmxvYXRRdWVzdGlvbjphY3Jvc3MtZW52aXJvbm1lbnQ=",
                                    "label": "Tyler Valencia",
                                    "slug": "across-environment",
                                }
                            }
                        ]
                    },
                    "slug": "effort-meet",
                }
            },
            {
                "node": {
                    "description": "Second result",
                    "id": "Rm9ybTpraXRjaGVuLWRldmVsb3A=",
                    "meta": {},
                    "name": "2nd",
                    "questions": {"edges": []},
                    "slug": "kitchen-develop",
                }
            },
            {
                "node": {
                    "description": "Second result",
                    "id": "Rm9ybTpzZXJ2aWNlLWJhbmstYXJt",
                    "meta": {},
                    "name": "3rd",
                    "questions": {"edges": []},
                    "slug": "service-bank-arm",
                }
            },
        ]
    }
}

snapshots["test_save_form[some description text-en] 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTplZmZvcnQtbWVldA==",
            "meta": {},
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}

snapshots["test_save_form[some description text-de] 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTplZmZvcnQtbWVldA==",
            "meta": {},
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}

snapshots["test_save_form[en] 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTplZmZvcnQtbWVldA==",
            "meta": {},
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}

snapshots["test_save_form[de] 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTplZmZvcnQtbWVldA==",
            "meta": {},
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}

snapshots["test_remove_form_question 1"] = {
    "removeFormQuestion": {
        "clientMutationId": None,
        "form": {"questions": {"edges": []}},
    }
}
