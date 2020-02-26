# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_query_all_questions[multiple_choice-search_value0-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"question": "multiple_choice", "value": ["a", "b"]}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-EXACT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "EXACT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-STARTSWITH] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "STARTSWITH",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): STARTSWITH']\")]",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-CONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "CONTAINS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-ICONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "ICONTAINS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "GTE", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): GTE']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "GT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): GT']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "LTE", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): LTE']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "LT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): LT']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"question": "multiple_choice", "value": ["a", "b"]}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "EXACT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-nomatch-STARTSWITH] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "STARTSWITH",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): STARTSWITH']\")]",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-nomatch-CONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "CONTAINS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-nomatch-ICONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "ICONTAINS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "GTE", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): GTE']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "GT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): GT']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "LTE", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): LTE']\")]",
    },
}

snapshots["test_query_all_questions[multiple_choice-search_value0-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "LT", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=multiple_choice (MULTIPLE_CHOICE): LT']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "DIRECT", "question": "integer", "value": 10}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "DIRECT", "question": "integer", "value": 10}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "DIRECT", "question": "text", "value": "foo"}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[text-foo-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[text-foo-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[text-foo-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[text-foo-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): GTE']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): GT']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): LTE']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): LT']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "DIRECT", "question": "text", "value": "foo"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): GTE']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): GT']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): LTE']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): LT']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"hierarchy": "FAMILY", "question": "textarea", "value": "foo"}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): GTE']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): GT']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): LTE']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): LT']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"hierarchy": "FAMILY", "question": "textarea", "value": "foo"}
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): GTE']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): GT']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): LTE']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): LT']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "FAMILY", "question": "float", "value": 11.5}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"hierarchy": "FAMILY", "question": "float", "value": 11.5}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-None] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-EXACT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-STARTSWITH] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-CONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-ICONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-GTE] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-GT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-LTE] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-LT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-None] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-EXACT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "EXACT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-STARTSWITH] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "STARTSWITH",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-CONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "CONTAINS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-ICONTAINS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ICONTAINS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-GTE] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GTE",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-GT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "GT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-LTE] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LTE",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-LT] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "LT",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"hierarchy": "DIRECT", "question": "date", "value": "2018-05-09"}
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"hierarchy": "DIRECT", "question": "date", "value": "2018-05-09"}
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "EXACT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "STARTSWITH",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "CONTAINS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): CONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ICONTAINS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GTE",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "GT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LTE",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "LT",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-matching-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {"hasAnswer": [{"question": "choice", "value": "a"}]},
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[choice-a-matching-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "EXACT", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[choice-a-matching-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "STARTSWITH", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "CONTAINS", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[choice-a-matching-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "ICONTAINS", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "GTE", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): GTE']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "GT", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): GT']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "LTE", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): LTE']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "LT", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): LT']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-None] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {"hasAnswer": [{"question": "choice", "value": "a"}]},
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-nomatch-EXACT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "EXACT", "question": "choice", "value": "a"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-nomatch-STARTSWITH] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "STARTSWITH", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): STARTSWITH']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-CONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "CONTAINS", "question": "choice", "value": "a"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-nomatch-ICONTAINS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "ICONTAINS", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): ICONTAINS']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-GTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "GTE", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): GTE']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-GT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "GT", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): GT']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-LTE] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "LTE", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): LTE']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-LT] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "LT", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=choice (CHOICE): LT']\")]",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-INTERSECTS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "INTERSECTS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-nomatch-INTERSECTS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "lookup": "INTERSECTS",
                    "question": "multiple_choice",
                    "value": ["a", "b"],
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[integer-10-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=integer (INTEGER): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[text-foo-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=text (TEXT): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[textarea-foo-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=textarea (TEXTAREA): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[float-11.5-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=float (FLOAT): INTERSECTS']\")]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-INTERSECTS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-INTERSECTS] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "INTERSECTS",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "INTERSECTS",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError(\"['Invalid lookup for question slug=date (DATE): INTERSECTS']\")]",
    },
}

snapshots["test_query_all_questions[choice-a-matching-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "INTERSECTS", "question": "choice", "value": "a"}]
        },
    },
    "response": {
        "data": {"allDocuments": {"edges": [{"node": {"form": {"slug": "subform"}}}]}},
        "errors": "None",
    },
}

snapshots["test_query_all_questions[choice-a-nomatch-INTERSECTS] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "INTERSECTS", "question": "choice", "value": "a"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-matching-ISNULL] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "ISNULL", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[multiple_choice-search_value0-nomatch-ISNULL] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {"lookup": "ISNULL", "question": "multiple_choice", "value": ["a", "b"]}
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[integer-10-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "integer",
                    "value": 10,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[text-foo-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "text",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[textarea-foo-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "textarea",
                    "value": "foo",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[float-11.5-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "float",
                    "value": 11.5,
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-matching-ISNULL] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots[
    "test_query_all_questions[datetime-2018-05-09T14:54:51.728786-nomatch-ISNULL] 1"
] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "FAMILY",
                    "lookup": "ISNULL",
                    "question": "datetime",
                    "value": "2018-05-09T14:54:51.728786",
                }
            ]
        },
    },
    "response": {
        "data": {"allDocuments": None},
        "errors": "[GraphQLLocatedError('Question matching query does not exist.')]",
    },
}

snapshots["test_query_all_questions[date-2018-05-09-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[date-2018-05-09-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [
                {
                    "hierarchy": "DIRECT",
                    "lookup": "ISNULL",
                    "question": "date",
                    "value": "2018-05-09",
                }
            ]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-matching-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "ISNULL", "question": "choice", "value": "a"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}

snapshots["test_query_all_questions[choice-a-nomatch-ISNULL] 1"] = {
    "request": {
        "query": """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """,
        "variables": {
            "hasAnswer": [{"lookup": "ISNULL", "question": "choice", "value": "a"}]
        },
    },
    "response": {"data": {"allDocuments": {"edges": []}}, "errors": "None"},
}
