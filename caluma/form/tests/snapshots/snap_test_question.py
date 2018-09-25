# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_questions[integer-question__configuration0] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "IntegerQuestion",
                    "id": "SW50ZWdlclF1ZXN0aW9uOk5vbmU=",
                    "integerMaxValue": 10,
                    "integerMinValue": 0,
                    "label": "Jordan Mccarthy",
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[float-question__configuration1] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FloatQuestion",
                    "floatMaxValue": 1.0,
                    "floatMinValue": 0.0,
                    "id": "RmxvYXRRdWVzdGlvbjpOb25l",
                    "label": "Jordan Mccarthy",
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[text-question__configuration2] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextQuestion",
                    "id": "VGV4dFF1ZXN0aW9uOk5vbmU=",
                    "label": "Jordan Mccarthy",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[textarea-question__configuration3] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextareaQuestion",
                    "id": "VGV4dGFyZWFRdWVzdGlvbjpOb25l",
                    "label": "Jordan Mccarthy",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "mrs-shake-recent",
                }
            }
        ]
    }
}

snapshots["test_save_float_question[float-question__configuration0] 1"] = {
    "data": {
        "saveFloatQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "FloatQuestion",
                "id": "RmxvYXRRdWVzdGlvbjpOb25l",
                "label": "Jordan Mccarthy",
                "maxValue": 10.0,
                "meta": "{}",
                "minValue": 0.0,
                "slug": "mrs-shake-recent",
            },
        }
    },
    "errors": [],
}

snapshots["test_save_integer_question[integer-question__configuration0] 1"] = {
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

snapshots["test_save_integer_question[integer-question__configuration1] 1"] = {
    "data": {"saveIntegerQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'non_field_errors': [ErrorDetail(string='max_value 1 is smaller than 10', code='invalid')]}",
            "path": ["saveIntegerQuestion"],
        }
    ],
}

snapshots["test_save_float_question[float-question__configuration1] 1"] = {
    "data": {"saveFloatQuestion": None},
    "errors": [
        {
            "locations": [{"column": 11, "line": 3}],
            "message": "{'non_field_errors': [ErrorDetail(string='max_value 1.0 is smaller than 10.0', code='invalid')]}",
            "path": ["saveFloatQuestion"],
        }
    ],
}

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
