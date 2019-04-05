# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_table_question[table] 1"] = {
    "saveTableQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "TableQuestion",
            "id": "VGFibGVRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
            "meta": {},
            "rowForm": {"slug": "effort-meet"},
            "slug": "sound-air-mission",
        },
    }
}

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
                    "meta": {},
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
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
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
                    "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_question[true-True-SaveTextQuestion] 1"] = {
    "saveTextQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "TextQuestion",
            "id": "VGV4dFF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_question[true-True-SaveTextareaQuestion] 1"] = {
    "saveTextareaQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "TextareaQuestion",
            "id": "VGV4dGFyZWFRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_question[true-True-SaveIntegerQuestion] 1"] = {
    "saveIntegerQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "IntegerQuestion",
            "id": "SW50ZWdlclF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_question[true-True-SaveFloatQuestion] 1"] = {
    "saveFloatQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "FloatQuestion",
            "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_float_question[float-question__configuration0-True] 1"] = {
    "saveFloatQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "FloatQuestion",
            "id": "RmxvYXRRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
            "maxValue": 10.0,
            "meta": {},
            "minValue": 0.0,
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_integer_question[integer-question__configuration0-True] 1"] = {
    "saveIntegerQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "IntegerQuestion",
            "id": "SW50ZWdlclF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_save_multiple_choice_question[multiple_choice] 1"] = {
    "saveMultipleChoiceQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "MultipleChoiceQuestion",
            "id": "TXVsdGlwbGVDaG9pY2VRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
            "label": "Thomas Johnson",
            "meta": {},
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

snapshots["test_save_choice_question[choice] 1"] = {
    "saveChoiceQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "ChoiceQuestion",
            "id": "Q2hvaWNlUXVlc3Rpb246c291bmQtYWlyLW1pc3Npb24=",
            "label": "Thomas Johnson",
            "meta": {},
            "options": {
                "edges": [
                    {"node": {"label": "Kelly Brock", "slug": "example-indicate"}}
                ]
            },
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_query_all_questions[text-question__configuration4] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextQuestion",
                    "id": "VGV4dFF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "label": "Thomas Johnson",
                    "maxLength": 10,
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[textarea-question__configuration5] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextareaQuestion",
                    "id": "VGV4dGFyZWFRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "maxLength": 10,
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[choice-question__configuration6] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "ChoiceQuestion",
                    "id": "Q2hvaWNlUXVlc3Rpb246c291bmQtYWlyLW1pc3Npb24=",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "options": {"edges": [{"node": {"slug": "example-indicate"}}]},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[multiple_choice-question__configuration7] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "MultipleChoiceQuestion",
                    "id": "TXVsdGlwbGVDaG9pY2VRdWVzdGlvbjpzb3VuZC1haXItbWlzc2lvbg==",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "options": {"edges": [{"node": {"slug": "example-indicate"}}]},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_query_all_questions[date-question__configuration3] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "DateQuestion",
                    "id": "RGF0ZVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_question[true-True-SaveDateQuestion] 1"] = {
    "saveDateQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "DateQuestion",
            "id": "RGF0ZVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}

snapshots["test_query_all_questions[form-question__configuration8] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FormQuestion",
                    "id": "Rm9ybVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_form_question[form] 1"] = {
    "saveFormQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "FormQuestion",
            "id": "Rm9ybVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
            "subForm": {"slug": "effort-meet"},
        },
    }
}

snapshots["test_query_all_questions[file-question__configuration9] 1"] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FileQuestion",
                    "id": "RmlsZVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
                    "label": "Thomas Johnson",
                    "meta": {},
                    "slug": "sound-air-mission",
                }
            }
        ]
    }
}

snapshots["test_save_question[true-True-SaveFileQuestion] 1"] = {
    "saveFileQuestion": {
        "clientMutationId": "testid",
        "question": {
            "__typename": "FileQuestion",
            "id": "RmlsZVF1ZXN0aW9uOnNvdW5kLWFpci1taXNzaW9u",
            "label": "Thomas Johnson",
            "meta": {},
            "slug": "sound-air-mission",
        },
    }
}
