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

snapshots["test_save_form[some description text] 1"] = {
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

snapshots["test_save_form[] 1"] = {
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

snapshots["test_query_all_forms 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "description": """Line whatever team suggest traditional boy. Drop argue move. Anyone remember prove.
Kid avoid player relationship to range whose. Draw free property consider.""",
                    "id": "Rm9ybTplZmZvcnQtbWVldA==",
                    "meta": "{}",
                    "name": "Brian Williams",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "VGV4dFF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                                    "label": "Thomas Johnson",
                                    "slug": "sound-air-mission",
                                }
                            }
                        ]
                    },
                    "slug": "effort-meet",
                }
            }
        ]
    }
}
