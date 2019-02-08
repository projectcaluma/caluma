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
                    "id": "SW50ZWdlclF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "integerMaxValue": 10,
                    "integerMinValue": 0,
                    "label": "Thomas Johnson",
                    "meta": "{}",
                    "slug": "sound-air-mission",
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
                    "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "meta": "{}",
                    "slug": "sound-air-mission",
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
                "id": "VGV4dFF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                "label": "Thomas Johnson",
                "meta": "{}",
                "slug": "sound-air-mission",
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
                "id": "VGV4dGFyZWFRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                "label": "Thomas Johnson",
                "meta": "{}",
                "slug": "sound-air-mission",
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
                "id": "SW50ZWdlclF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                "label": "Thomas Johnson",
                "meta": "{}",
                "slug": "sound-air-mission",
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
                "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                "label": "Thomas Johnson",
                "meta": "{}",
                "slug": "sound-air-mission",
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
                "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                "label": "Thomas Johnson",
                "maxValue": 10.0,
                "meta": "{}",
                "minValue": 0.0,
                "slug": "sound-air-mission",
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
                "id": "SW50ZWdlclF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                "label": "Thomas Johnson",
                "meta": "{}",
                "slug": "sound-air-mission",
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

snapshots["test_query_all_questions[float-question__configuration2] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FloatQuestion",
                    "floatMaxValue": None,
                    "floatMinValue": None,
                    "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "meta": "{}",
                    "slug": "sound-air-mission",
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
                    "id": "VGV4dFF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "label": "Thomas Johnson",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "sound-air-mission",
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
                    "id": "VGV4dGFyZWFRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "maxLength": 10,
                    "meta": "{}",
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[choice-question__configuration5] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "ChoiceQuestion",
                    "id": "Q2hvaWNlUXVlc3Rpb246c291bmQtYWlyLW1pc3Npb24=",
                    "label": "Thomas Johnson",
                    "meta": "{}",
                    "options": {"edges": [{"node": {"slug": "example-indicate"}}]},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_choice_question[choice] 1"] = {
    "saveChoiceQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "ChoiceQuestion",
            "id": "Q2hvaWNlUXVlc3Rpb246c291bmQtYWlyLW1pc3Npb24=",
            "label": "Thomas Johnson",
            "meta": "{}",
            "options": {
                "edges": [
                    {"node": {"label": "Kelly Brock", "slug": "example-indicate"}}
                ]
            },
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_query_all_questions[multiple_choice-question__configuration6] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "MultipleChoiceQuestion",
                    "id": "TXVsdGlwbGVDaG9pY2VRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "meta": "{}",
                    "options": {"edges": [{"node": {"slug": "example-indicate"}}]},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_multiple_choice_question[multiple_choice] 1"] = {
    "saveMultipleChoiceQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "MultipleChoiceQuestion",
            "id": "TXVsdGlwbGVDaG9pY2VRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
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
            "slug": "sound-air-mission",
        },
    }
}
