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

snapshots["test_add_form_question[True] 1"] = {
    "data": {"addFormQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "Form mrs-shake-recent may not be edited as it is archived or published",
            "path": ["addFormQuestion"],
        }
    ],
}

snapshots["test_add_form_question[False] 1"] = {
    "data": {
        "addFormQuestion": {
            "clientMutationId": None,
            "form": {"questions": {"edges": [{"node": {"slug": "rather-cost-admit"}}]}},
        }
    },
    "errors": [],
}

snapshots["test_remove_form_question[True] 1"] = {
    "data": {"removeFormQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "Form mrs-shake-recent may not be edited as it is archived or published",
            "path": ["removeFormQuestion"],
        }
    ],
}

snapshots["test_remove_form_question[False] 1"] = {
    "data": {
        "removeFormQuestion": {
            "clientMutationId": None,
            "form": {"questions": {"edges": []}},
        }
    },
    "errors": [],
}
