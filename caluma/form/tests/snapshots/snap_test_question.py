# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_question[true-SaveTextQuestion] 1"] = {
    "data": {
        "saveTextQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "TextQuestion",
                "id": "VGV4dFF1ZXN0aW9uOk5vbmU=",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true-SaveTextareaQuestion] 1"] = {
    "data": {
        "saveTextareaQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "TextareaQuestion",
                "id": "VGV4dGFyZWFRdWVzdGlvbjpOb25l",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true-SaveCheckboxQuestion] 1"] = {
    "data": {
        "saveCheckboxQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "CheckboxQuestion",
                "id": "Q2hlY2tib3hRdWVzdGlvbjpOb25l",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true-SaveRadioQuestion] 1"] = {
    "data": {
        "saveRadioQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "RadioQuestion",
                "id": "UmFkaW9RdWVzdGlvbjpOb25l",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true-SaveIntegerQuestion] 1"] = {
    "data": {
        "saveIntegerQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "IntegerQuestion",
                "id": "SW50ZWdlclF1ZXN0aW9uOk5vbmU=",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true-SaveFloatQuestion] 1"] = {
    "data": {
        "saveFloatQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "FloatQuestion",
                "id": "RmxvYXRRdWVzdGlvbjpOb25l",
                "label": "Jordan Mccarthy",
                "meta": "{}",
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_question[true|invalid-SaveTextQuestion] 1"] = {
    "data": {"saveTextQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveTextQuestion"],
        }
    ],
}

snapshots["test_save_question[true|invalid-SaveTextareaQuestion] 1"] = {
    "data": {"saveTextareaQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveTextareaQuestion"],
        }
    ],
}

snapshots["test_save_question[true|invalid-SaveCheckboxQuestion] 1"] = {
    "data": {"saveCheckboxQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveCheckboxQuestion"],
        }
    ],
}

snapshots["test_save_question[true|invalid-SaveRadioQuestion] 1"] = {
    "data": {"saveRadioQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveRadioQuestion"],
        }
    ],
}

snapshots["test_save_question[true|invalid-SaveIntegerQuestion] 1"] = {
    "data": {"saveIntegerQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveIntegerQuestion"],
        }
    ],
}

snapshots["test_save_question[true|invalid-SaveFloatQuestion] 1"] = {
    "data": {"saveFloatQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'is_required': [ErrorDetail(string='The `invalid` transform is undefined.', code='invalid')]}",
            "path": ["saveFloatQuestion"],
        }
    ],
}

snapshots["test_query_all_questions 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "id": "Q2hlY2tib3hRdWVzdGlvbjpOb25l",
                    "label": "Jordan Mccarthy",
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}
