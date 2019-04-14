# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_documents[integer-1-None] 1"] = {
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

snapshots["test_query_all_documents[float-2.1-None] 1"] = {
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

snapshots["test_query_all_documents[text-somevalue-None] 1"] = {
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

snapshots["test_query_all_documents[multiple_choice-answer__value3-None] 1"] = {
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

snapshots["test_query_all_documents[table-None-None] 1"] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "TableAnswer",
                                    "question": {
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                    "table_value": [{"form": {"slug": "effort-meet"}}],
                                }
                            }
                        ]
                    },
                    "createdByUser": "872d1b6f-790c-473c-b5e9-2e714d607695",
                }
            }
        ]
    }
}

snapshots["test_query_all_documents[date-None-2019-02-22] 1"] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "DateAnswer",
                                    "date_value": "2019-02-22",
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

snapshots["test_query_all_documents[file-some-file.pdf-None] 1"] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "FileAnswer",
                                    "fileValue": {
                                        "downloadUrl": "http://minio/download-url",
                                        "metadata": {
                                            "bucket_name": "caluma-media",
                                            "content_type": "application/pdf",
                                            "etag": "0c81da684e6aaef48e8f3113e5b8769b",
                                            "is_dir": False,
                                            "last_modified": (
                                                2019,
                                                4,
                                                5,
                                                7,
                                                0,
                                                49,
                                                4,
                                                95,
                                                0,
                                            ),
                                            "metadata": {
                                                "X-Amz-Meta-Testtag": "super_file"
                                            },
                                            "object_name": "some-file.pdf",
                                            "size": 8200,
                                        },
                                        "name": "some-file.pdf",
                                    },
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

snapshots["test_query_all_documents[file-some-other-file.pdf-None] 1"] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "FileAnswer",
                                    "fileValue": {
                                        "downloadUrl": "http://minio/download-url",
                                        "metadata": {
                                            "bucket_name": "caluma-media",
                                            "content_type": "application/pdf",
                                            "etag": "0c81da684e6aaef48e8f3113e5b8769b",
                                            "is_dir": False,
                                            "last_modified": (
                                                2019,
                                                4,
                                                5,
                                                7,
                                                0,
                                                49,
                                                4,
                                                95,
                                                0,
                                            ),
                                            "metadata": {
                                                "X-Amz-Meta-Testtag": "super_file"
                                            },
                                            "object_name": "some-file.pdf",
                                            "size": 8200,
                                        },
                                        "name": "some-other-file.pdf",
                                    },
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
    "test_save_document_answer[integer-question__configuration0-1-None-SaveDocumentIntegerAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[integer-question__configuration0-1-None-SaveDocumentIntegerAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-2.1-None-SaveDocumentFloatAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"floatValue": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-2.1-None-SaveDocumentFloatAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"floatValue": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-Test-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-Test-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[date-question__configuration7-None-2019-02-22-SaveDocumentDateAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentDateAnswer": {
        "answer": {"dateValue": "2019-02-22"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[date-question__configuration7-None-2019-02-22-SaveDocumentDateAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentDateAnswer": {
        "answer": {"dateValue": "2019-02-22"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration9-some-file.pdf-None-SaveDocumentFileAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "fileValue": {
                "name": "some-file.pdf",
                "uploadUrl": "http://minio/upload-url",
            }
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration9-some-file.pdf-None-SaveDocumentFileAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {"stringValue": "some-file.pdf"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration10-not-exist.pdf-None-SaveDocumentFileAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "fileValue": {
                "name": "not-exist.pdf",
                "uploadUrl": "http://minio/upload-url",
            }
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration10-not-exist.pdf-None-SaveDocumentFileAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {"stringValue": "not-exist.pdf"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[table-question__configuration12-None-None-SaveDocumentTableAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentTableAnswer": {
        "answer": {
            "table_value": [
                {"form": {"slug": "suggest-traditional"}},
                {"form": {"slug": "suggest-traditional"}},
            ]
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[table-question__configuration12-None-None-SaveDocumentTableAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentTableAnswer": {
        "answer": {
            "table_value": [
                {"form": {"slug": "suggest-traditional"}},
                {"form": {"slug": "suggest-traditional"}},
            ]
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration14-Test-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration14-Test-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[multiple_choice-question__configuration16-answer__value16-None-SaveDocumentListAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[multiple_choice-question__configuration16-answer__value16-None-SaveDocumentListAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[choice-question__configuration18-option-slug-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[choice-question__configuration18-option-slug-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[form-question__configuration13-None-None-SaveDocumentFormAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFormAnswer": {
        "answer": {"form_value": {"form": {"slug": "suggest-traditional"}}},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[form-question__configuration13-None-None-SaveDocumentFormAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFormAnswer": {
        "answer": {"form_value": {"form": {"slug": "suggest-traditional"}}},
        "clientMutationId": "testid",
    }
}
