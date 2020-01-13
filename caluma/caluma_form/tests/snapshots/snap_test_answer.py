# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_remove_answer[integer-23] 1"] = {
    "removeAnswer": {
        "answer": {
            "__typename": "IntegerAnswer",
            "id": "SW50ZWdlckFuc3dlcjpOb25l",
            "meta": {},
        },
        "clientMutationId": None,
    }
}
