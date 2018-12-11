# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_add_form_question 1"] = {
    "data": {
        "addFormQuestion": {
            "clientMutationId": None,
            "form": {"questions": {"edges": [{"node": {"slug": "sound-air-mission"}}]}},
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

snapshots["test_query_all_forms[First result] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "description": "First result",
                    "id": "Rm9ybTplZmZvcnQtbWVldA==",
                    "meta": "{}",
                    "name": "Brian Williams",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "VGV4dGFyZWFRdWVzdGlvbjpzdWdnZXN0LXRyYWRpdGlvbmFs",
                                    "label": "John Thomas",
                                    "slug": "suggest-traditional",
                                }
                            }
                        ]
                    },
                    "slug": "effort-meet",
                }
            },
            {
                "node": {
                    "description": "Seconds result",
                    "id": "Rm9ybTpzZXJ2aWNlLWJhbmstYXJt",
                    "meta": "{}",
                    "name": "Brian Williams",
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
            "meta": "{}",
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
            "meta": "{}",
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
            "meta": "{}",
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
            "meta": "{}",
            "name": "Brian Williams",
            "slug": "effort-meet",
        },
    }
}
