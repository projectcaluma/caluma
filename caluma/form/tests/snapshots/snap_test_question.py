# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_question[true|invalid] 1"] = {
    "data": {"saveQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveQuestion"],
        }
    ],
}

snapshots["test_save_question[true] 1"] = {
    "data": {
        "saveQuestion": {
            "clientMutationId": "testid",
            "question": {
                "configuration": "{}",
                "id": "UXVlc3Rpb246bXJzLXNoYWtlLXJlY2VudA==",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
                "type": "CHECKBOX",
            },
        }
    },
    "errors": [],
}

snapshots["test_query_all_questions 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "configuration": "{}",
                    "id": "UXVlc3Rpb246bXJzLXNoYWtlLXJlY2VudA==",
                    "label": "Jordan Mccarthy",
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                    "type": "CHECKBOX",
                }
            }
        ]
    }
}
