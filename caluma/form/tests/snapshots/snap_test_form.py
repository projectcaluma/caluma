# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_forms[integer-1] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "IntegerAnswer",
                                    "integer_value": 1,
                                    "question": {
                                        "label": "Amanda Boyd",
                                        "slug": "fly-even-yourself",
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
}

snapshots["test_query_all_forms[float-2.1] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "FloatAnswer",
                                    "float_value": 2.1,
                                    "question": {
                                        "label": "Amanda Boyd",
                                        "slug": "fly-even-yourself",
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
}

snapshots["test_query_all_forms[text-somevalue] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "StringAnswer",
                                    "question": {
                                        "label": "Amanda Boyd",
                                        "slug": "fly-even-yourself",
                                    },
                                    "string_value": "somevalue",
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
}

snapshots["test_query_all_forms[checkbox-answer__value3] 1"] = {
    "allForms": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "ListAnswer",
                                    "list_value": ["somevalue", "anothervalue"],
                                    "question": {
                                        "label": "Amanda Boyd",
                                        "slug": "fly-even-yourself",
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
}

snapshots["test_save_form 1"] = {
    "saveForm": {
        "clientMutationId": "testid",
        "form": {"formSpecification": {"slug": "mrs-shake-recent"}},
    }
}

snapshots[
    "test_save_form_answer[integer-question__configuration0-1-SaveFormIntegerAnswer-True-option-slug] 1"
] = {
    "saveFormIntegerAnswer": {
        "answer": {"integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_form_answer[float-question__configuration2-2.1-SaveFormFloatAnswer-True-option-slug] 1"
] = {
    "saveFormFloatAnswer": {"answer": {"floatValue": 2.1}, "clientMutationId": "testid"}
}

snapshots[
    "test_save_form_answer[text-question__configuration4-Test-SaveFormStringAnswer-True-option-slug] 1"
] = {
    "saveFormStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_form_answer[checkbox-question__configuration7-answer__value7-SaveFormListAnswer-True-option-slug] 1"
] = {
    "saveFormListAnswer": {
        "answer": {"listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_form_answer[radio-question__configuration9-option-slug-SaveFormStringAnswer-True-option-slug] 1"
] = {
    "saveFormStringAnswer": {
        "answer": {"stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}
