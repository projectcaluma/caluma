# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_query_all_documents[integer-None-1-None] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[float-None-2.1-None] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[text-None-somevalue-None] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[multiple_choice-None-answer__value3-None] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[table-None-None-None] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "872d1b6f-790c-473c-b5e9-2e714d607695",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[date-None-None-2019-02-22] 1"] = {
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[file-None-some-file.pdf-None] 1"] = {
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
                                        "downloadUrl": "http://minio/download-url/09c697fb-fd0a-4345-bb9c-99df350b0cdb_some-file.pdf",
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[file-None-some-other-file.pdf-None] 1"] = {
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
                                        "downloadUrl": "http://minio/download-url/09c697fb-fd0a-4345-bb9c-99df350b0cdb_some-other-file.pdf",
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
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots["test_query_all_documents[dynamic_choice-MyDataSource-5.5-None] 1"] = {
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
                                    "string_value": "5.5",
                                }
                            }
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_query_all_documents[dynamic_multiple_choice-MyDataSource-answer__value9-None] 1"
] = {
    "allDocuments": {
        "edges": [
            {
                "node": {
                    "answers": {
                        "edges": [
                            {
                                "node": {
                                    "__typename": "ListAnswer",
                                    "list_value": ["5.5"],
                                    "question": {
                                        "label": "Thomas Johnson",
                                        "slug": "sound-air-mission",
                                    },
                                }
                            }
                        ],
                        "totalCount": 1,
                    },
                    "createdByUser": "b24d3781-2f59-44c4-8602-cffe6aa89ae7",
                }
            }
        ],
        "totalCount": 1,
    }
}

snapshots[
    "test_save_document_answer[integer-question__configuration0-None-question__format_validators0-1-None-SaveDocumentIntegerAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"__typename": "IntegerAnswer", "integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[integer-question__configuration0-None-question__format_validators0-1-None-SaveDocumentIntegerAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentIntegerAnswer": {
        "answer": {"__typename": "IntegerAnswer", "integerValue": 1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-None-question__format_validators2-2.1-None-SaveDocumentFloatAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"__typename": "FloatAnswer", "floatValue": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[float-question__configuration2-None-question__format_validators2-2.1-None-SaveDocumentFloatAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFloatAnswer": {
        "answer": {"__typename": "FloatAnswer", "floatValue": 2.1},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-None-question__format_validators4-Test-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration4-None-question__format_validators4-Test-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[date-question__configuration7-None-question__format_validators7-None-2019-02-22-SaveDocumentDateAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentDateAnswer": {
        "answer": {"__typename": "DateAnswer", "dateValue": "2019-02-22"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[date-question__configuration7-None-question__format_validators7-None-2019-02-22-SaveDocumentDateAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentDateAnswer": {
        "answer": {"__typename": "DateAnswer", "dateValue": "2019-02-22"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration9-None-question__format_validators9-some-file.pdf-None-SaveDocumentFileAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "__typename": "FileAnswer",
            "fileValue": {
                "name": "some-file.pdf",
                "uploadUrl": "http://minio/upload-url",
            },
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration9-None-question__format_validators9-some-file.pdf-None-SaveDocumentFileAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "__typename": "FileAnswer",
            "fileValue": {
                "name": "some-file.pdf",
                "uploadUrl": "http://minio/upload-url",
            },
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration10-None-question__format_validators10-not-exist.pdf-None-SaveDocumentFileAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "__typename": "FileAnswer",
            "fileValue": {
                "name": "not-exist.pdf",
                "uploadUrl": "http://minio/upload-url",
            },
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[file-question__configuration10-None-question__format_validators10-not-exist.pdf-None-SaveDocumentFileAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentFileAnswer": {
        "answer": {
            "__typename": "FileAnswer",
            "fileValue": {
                "name": "not-exist.pdf",
                "uploadUrl": "http://minio/upload-url",
            },
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[table-question__configuration12-None-question__format_validators12-None-None-SaveDocumentTableAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentTableAnswer": {
        "answer": {
            "__typename": "TableAnswer",
            "table_value": [
                {"form": {"slug": "suggest-traditional"}},
                {"form": {"slug": "suggest-traditional"}},
            ],
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[table-question__configuration12-None-question__format_validators12-None-None-SaveDocumentTableAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentTableAnswer": {
        "answer": {
            "__typename": "TableAnswer",
            "table_value": [
                {"form": {"slug": "suggest-traditional"}},
                {"form": {"slug": "suggest-traditional"}},
            ],
        },
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration13-None-question__format_validators13-Test-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration13-None-question__format_validators13-Test-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "Test"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[multiple_choice-question__configuration15-None-question__format_validators15-answer__value15-None-SaveDocumentListAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"__typename": "ListAnswer", "listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[multiple_choice-question__configuration15-None-question__format_validators15-answer__value15-None-SaveDocumentListAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"__typename": "ListAnswer", "listValue": ["option-slug"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[choice-question__configuration17-None-question__format_validators17-option-slug-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[choice-question__configuration17-None-question__format_validators17-option-slug-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "option-slug"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[dynamic_multiple_choice-question__configuration19-MyDataSource-question__format_validators19-answer__value19-None-SaveDocumentListAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"__typename": "ListAnswer", "listValue": ["5.5", "1"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[dynamic_multiple_choice-question__configuration19-MyDataSource-question__format_validators19-answer__value19-None-SaveDocumentListAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentListAnswer": {
        "answer": {"__typename": "ListAnswer", "listValue": ["5.5", "1"]},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[dynamic_choice-question__configuration21-MyDataSource-question__format_validators21-5.5-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "5.5"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[dynamic_choice-question__configuration21-MyDataSource-question__format_validators21-5.5-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "5.5"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration24-None-question__format_validators24-test@example.com-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[text-question__configuration24-None-question__format_validators24-test@example.com-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration26-None-question__format_validators26-test@example.com-None-SaveDocumentStringAnswer-True-option-slug-True] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_save_document_answer[textarea-question__configuration26-None-question__format_validators26-test@example.com-None-SaveDocumentStringAnswer-True-option-slug-False] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots["test_save_document_answer_empty[text-false-None-True] 1"] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": None},
        "clientMutationId": None,
    }
}

snapshots["test_save_document_answer_empty[text-false-None-False] 1"] = {
    "saveDocumentStringAnswer": {
        "answer": {"__typename": "StringAnswer", "stringValue": None},
        "clientMutationId": None,
    }
}
