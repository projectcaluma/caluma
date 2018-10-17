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
                    "id": "SW50ZWdlclF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "integerMaxValue": 10,
                    "integerMinValue": 0,
                    "label": "Brian Williams",
                    "meta": "{}",
                    "slug": "effort-meet",
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
                    "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "label": "Brian Williams",
                    "meta": "{}",
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_save_question[true-SaveTextQuestion] 1"] = {
    "data": {
        "saveTextQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "TextQuestion",
                "id": "VGV4dFF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                "label": "Brian Williams",
                "meta": "{}",
                "slug": "effort-meet",
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
                "id": "VGV4dGFyZWFRdWVzdGlvbjplZmZvcnQtbWVldA==",
                "label": "Brian Williams",
                "meta": "{}",
                "slug": "effort-meet",
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
                "id": "SW50ZWdlclF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                "label": "Brian Williams",
                "meta": "{}",
                "slug": "effort-meet",
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
                "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                "label": "Brian Williams",
                "meta": "{}",
                "slug": "effort-meet",
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

snapshots["test_save_float_question[float-question__configuration0] 1"] = {
    "data": {
        "saveFloatQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "FloatQuestion",
                "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                "label": "Brian Williams",
                "maxValue": 10.0,
                "meta": "{}",
                "minValue": 0.0,
                "slug": "effort-meet",
            },
        }
    },
    "errors": [],
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

snapshots["test_save_integer_question[integer-question__configuration0] 1"] = {
    "data": {
        "saveIntegerQuestion": {
            "clientMutationId": "testid",
            "question": {
                "__typename": "IntegerQuestion",
                "id": "SW50ZWdlclF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                "label": "Brian Williams",
                "meta": "{}",
                "slug": "effort-meet",
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

snapshots["test_save_checkbox_question[checkbox] 1"] = {
    "saveCheckboxQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "CheckboxQuestion",
            "id": "Q2hlY2tib3hRdWVzdGlvbjplZmZvcnQtbWVldA==",
            "label": "Brian Williams",
            "meta": "{}",
            "options": {
                "edges": [
                    {
                        "node": {
                            "label": "Mariah Reynolds",
                            "slug": "provide-beyond-seek",
                        }
                    },
                    {"node": {"label": "Daniel Mann", "slug": "live-by-itself"}},
                ]
            },
            "slug": "effort-meet",
        },
    }
}

snapshots["test_save_radio_question[radio] 1"] = {
    "saveRadioQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "RadioQuestion",
            "id": "UmFkaW9RdWVzdGlvbjplZmZvcnQtbWVldA==",
            "label": "Brian Williams",
            "meta": "{}",
            "options": {
                "edges": [
                    {"node": {"label": "John Thomas", "slug": "suggest-traditional"}}
                ]
            },
            "slug": "effort-meet",
        },
    }
}

snapshots["test_query_all_questions[float-question__configuration2] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FloatQuestion",
                    "floatMaxValue": None,
                    "floatMinValue": None,
                    "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "label": "Brian Williams",
                    "meta": "{}",
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[text-question__configuration3] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextQuestion",
                    "id": "VGV4dFF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "label": "Brian Williams",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[textarea-question__configuration4] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextareaQuestion",
                    "id": "VGV4dGFyZWFRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "label": "Brian Williams",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[radio-question__configuration5] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "RadioQuestion",
                    "id": "UmFkaW9RdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "label": "Brian Williams",
                    "meta": "{}",
                    "options": {"edges": [{"node": {"slug": "treatment-radio"}}]},
                    "slug": "effort-meet",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[checkbox-question__configuration6] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "CheckboxQuestion",
                    "id": "Q2hlY2tib3hRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "label": "Brian Williams",
                    "meta": "{}",
                    "options": {"edges": [{"node": {"slug": "treatment-radio"}}]},
                    "slug": "effort-meet",
                }
            }
        ]
    }
}
