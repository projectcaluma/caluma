# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_task_specifications 1"] = {
    "allTaskSpecifications": {
        "edges": [
            {
                "node": {
                    "description": """First where during teach country talk across. Little central meeting anyone remember.
Material minute ago get. Range whose scientist draw free property consider. Have director true force.""",
                    "meta": "{}",
                    "name": "Jordan Mccarthy",
                    "slug": "mrs-shake-recent",
                    "type": "SIMPLE",
                }
            }
        ]
    }
}

snapshots["test_save_task_specification 1"] = {
    "data": {
        "saveTaskSpecification": {
            "clientMutationId": "testid",
            "taskSpecification": {
                "meta": "{}",
                "name": "Jordan Mccarthy",
                "slug": "mrs-shake-recent",
                "type": "SIMPLE",
            },
        }
    },
    "errors": [],
}
