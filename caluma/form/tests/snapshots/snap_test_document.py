# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_document 1"] = {
    "saveDocument": {
        "clientMutationId": "testid",
        "document": {"form": {"slug": "effort-meet"}},
    }
}

snapshots[
    "test_save_document_answer[integer-question__configuration0-1-SaveDocumentIntegerAnswer-True-option-slug] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-2.1-SaveDocumentFloatAnswer-True-option-slug] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"floatValue": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots["test_query_all_documents[integer-1] 1"] = {
    "allDocuments": {
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
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                }
                            }
                        ]
                    },
                    "createdByUser": "4602cffe-6aa8-4ae7-ba6b-2cf34839ef47",
                }
            }
        ]
    }
}

snapshots["test_query_all_documents[float-2.1] 1"] = {
    "allDocuments": {
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
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                }
                            }
                        ]
                    },
                    "createdByUser": "4602cffe-6aa8-4ae7-ba6b-2cf34839ef47",
                }
            }
        ]
    }
}

snapshots["test_query_all_documents[text-somevalue] 1"] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "StringAnswer",
                                    "question": {
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                    "string_value": "somevalue",
                                }
                            }
                        ]
                    },
                    "createdByUser": "4602cffe-6aa8-4ae7-ba6b-2cf34839ef47",
                }
            }
        ]
    }
}

snapshots["test_query_all_documents[checkbox-answer__value3] 1"] = {
    "allDocuments": {
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
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                }
                            }
                        ]
                    },
                    "createdByUser": "4602cffe-6aa8-4ae7-ba6b-2cf34839ef47",
                }
            }
        ]
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-Test-SaveDocumentStringAnswer-True-option-slug] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[checkbox-question__configuration7-answer__value7-SaveDocumentListAnswer-True-option-slug] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[radio-question__configuration9-option-slug-SaveDocumentStringAnswer-True-option-slug] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}
