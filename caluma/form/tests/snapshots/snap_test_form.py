# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_delete_form 1"] = {
    "deleteForm": {
        "clientMutationId": "testid",
        "form": {
            "id": "Rm9ybTptcnMtc2hha2UtcmVjZW50",
            "meta": "{}",
            "name": "Jordan Mccarthy",
            "slug": "mrs-shake-recent",
        },
    }
}

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
