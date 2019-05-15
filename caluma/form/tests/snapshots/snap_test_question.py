# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots[
    "test_query_all_questions[integer-question__configuration0-None-question__format_validators0] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "IntegerQuestion",
                    "id": "SW50ZWdlclF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "integerMaxValue": 10,
                    "integerMinValue": 0,
                    "label": "Brian Williams",
                    "meta": {},
                    "placeholder": "",
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[float-question__configuration1-None-question__format_validators1] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FloatQuestion",
                    "floatMaxValue": 1.0,
                    "floatMinValue": 0.0,
                    "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "placeholder": "",
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[float-question__configuration2-None-question__format_validators2] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FloatQuestion",
                    "floatMaxValue": None,
                    "floatMinValue": None,
                    "id": "RmxvYXRRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "placeholder": "",
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[date-question__configuration3-None-question__format_validators3] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "DateQuestion",
                    "id": "RGF0ZVF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[text-question__configuration4-None-question__format_validators4] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextQuestion",
                    "formatValidators": {
                        "edges": [
                            {
                                "node": {
                                    "errorMsg": "Please enter a valid Email address.",
                                    "name": "E-mail",
                                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                                    "slug": "email",
                                }
                            }
                        ]
                    },
                    "id": "VGV4dFF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "label": "Brian Williams",
                    "maxLength": 10,
                    "meta": {},
                    "placeholder": "",
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[textarea-question__configuration5-None-question__format_validators5] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "TextareaQuestion",
                    "formatValidators": {"edges": []},
                    "id": "VGV4dGFyZWFRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "infoText": "",
                    "label": "Brian Williams",
                    "maxLength": 10,
                    "meta": {},
                    "placeholder": "",
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[choice-question__configuration6-None-question__format_validators6] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "ChoiceQuestion",
                    "id": "Q2hvaWNlUXVlc3Rpb246ZWZmb3J0LW1lZXQ=",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "options": {
                        "edges": [{"node": {"slug": "treatment-radio"}}],
                        "totalCount": 1,
                    },
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[multiple_choice-question__configuration7-None-question__format_validators7] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "MultipleChoiceQuestion",
                    "id": "TXVsdGlwbGVDaG9pY2VRdWVzdGlvbjplZmZvcnQtbWVldA==",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "options": {
                        "edges": [{"node": {"slug": "treatment-radio"}}],
                        "totalCount": 1,
                    },
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[form-question__configuration8-None-question__format_validators8] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FormQuestion",
                    "id": "Rm9ybVF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "slug": "effort-meet",
                    "subForm": {"slug": "suggest-traditional"},
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[file-question__configuration9-None-question__format_validators9] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "FileQuestion",
                    "id": "RmlsZVF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[dynamic_choice-question__configuration10-MyDataSource-question__format_validators10] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "DynamicChoiceQuestion",
                    "id": "RHluYW1pY0Nob2ljZVF1ZXN0aW9uOmVmZm9ydC1tZWV0",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "options": {
                        "edges": [
                            {"node": {"label": "1", "slug": "1"}},
                            {"node": {"label": "5.5", "slug": "5.5"}},
                            {"node": {"label": "sdkj", "slug": "sdkj"}},
                            {"node": {"label": "info", "slug": "value"}},
                            {"node": {"label": "something", "slug": "something"}},
                            {
                                "node": {
                                    "label": "english description",
                                    "slug": "translated_value",
                                }
                            },
                        ]
                    },
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[dynamic_multiple_choice-question__configuration11-MyDataSource-question__format_validators11] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "DynamicMultipleChoiceQuestion",
                    "id": "RHluYW1pY011bHRpcGxlQ2hvaWNlUXVlc3Rpb246ZWZmb3J0LW1lZXQ=",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "options": {
                        "edges": [
                            {"node": {"label": "1", "slug": "1"}},
                            {"node": {"label": "5.5", "slug": "5.5"}},
                            {"node": {"label": "sdkj", "slug": "sdkj"}},
                            {"node": {"label": "info", "slug": "value"}},
                            {"node": {"label": "something", "slug": "something"}},
                            {
                                "node": {
                                    "label": "english description",
                                    "slug": "translated_value",
                                }
                            },
                        ]
                    },
                    "slug": "effort-meet",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_questions[static-question__configuration12-None-question__format_validators12] 1"
] = {
    "allQuestions": {
        "edges": [
            {
                "node": {
                    "__typename": "StaticQuestion",
                    "id": "U3RhdGljUXVlc3Rpb246ZWZmb3J0LW1lZXQ=",
                    "infoText": "",
                    "label": "Brian Williams",
                    "meta": {},
                    "slug": "effort-meet",
                    "staticContent": """Line whatever team suggest traditional boy. Drop argue move. Anyone remember prove.
Kid avoid player relationship to range whose. Draw free property consider.""",
                }
            }
        ],
        "totalCount": 1,
    }
}
