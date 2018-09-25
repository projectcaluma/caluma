# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

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

snapshots["test_save_document 1"] = {
    "saveDocument": {
        "clientMutationId": "testid",
        "document": {"form": {"slug": "mrs-shake-recent"}},
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

snapshots[
    "test_save_document_answer[integer-question__configuration0-1-SaveDocumentIntegerAnswer-True] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"integer_value": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-2.1-SaveDocumentFloatAnswer-True] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"float_value": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-Test-SaveDocumentStringAnswer-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"string_value": '"Test"'},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[checkbox-question__configuration6-answer__value6-SaveDocumentListAnswer-True] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"list_value": ['["123", "1"]']},
        "clientMutationId": "testid",
    }
}
