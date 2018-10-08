# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_form_specifications 1"] = {
    "allFormSpecifications": {
        "edges": [
            {
                "node": {
                    "description": """Story first where during teach.
Across drop argue move. Anyone remember prove.
Kid avoid player relationship to range whose. Draw free property consider.""",
                    "id": "Rm9ybVNwZWNpZmljYXRpb246bXJzLXNoYWtlLXJlY2VudA==",
                    "meta": "{}",
                    "name": "Jordan Mccarthy",
                    "questions": {
                        "edges": [
                            {
                                "node": {
                                    "id": "UmFkaW9RdWVzdGlvbjpOb25l",
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

snapshots["test_save_form_specification[some description text] 1"] = {
    "saveFormSpecification": {
        "clientMutationId": "testid",
        "formSpecification": {
            "id": "Rm9ybVNwZWNpZmljYXRpb246bXJzLXNoYWtlLXJlY2VudA==",
            "meta": "{}",
            "name": "Jordan Mccarthy",
            "slug": "mrs-shake-recent",
        },
    }
}

snapshots["test_save_form_specification[] 1"] = {
    "saveFormSpecification": {
        "clientMutationId": "testid",
        "formSpecification": {
            "id": "Rm9ybVNwZWNpZmljYXRpb246bXJzLXNoYWtlLXJlY2VudA==",
            "meta": "{}",
            "name": "Jordan Mccarthy",
            "slug": "mrs-shake-recent",
        },
    }
}

snapshots["test_add_form_specification_question 1"] = {
    "data": {
        "addFormSpecificationQuestion": {
            "clientMutationId": None,
            "formSpecification": {
                "questions": {"edges": [{"node": {"slug": "fly-even-yourself"}}]}
            },
        }
    },
    "errors": [],
}

snapshots["test_remove_form_specification_question 1"] = {
    "removeFormSpecificationQuestion": {
        "clientMutationId": None,
        "formSpecification": {"questions": {"edges": []}},
    }
}
