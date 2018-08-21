# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_question[true] 1"] = {
    "data": {
        "saveQuestion": {
            "clientMutationId": None,
            "question": {
                "configuration": "{}",
                "id": "UXVlc3Rpb246bXJzLXNoYWtlLXJlY2VudA==",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
                "type": "NUMBER",
            },
        }
    },
    "errors": None,
}

snapshots["test_save_question[true|invalid] 1"] = {
    "data": {"saveQuestion": {"clientMutationId": None, "question": None}},
    "errors": None,
}
