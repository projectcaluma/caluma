# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "test_base_format_validators[question__format_validators1-test@example.com-True-text] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_base_format_validators[question__format_validators1-test@example.com-True-textarea] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "test@example.com"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_base_format_validators[question__format_validators3-+411234567890-True-text] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "+411234567890"},
        "clientMutationId": "testid",
    }
}

snapshots[
    "test_base_format_validators[question__format_validators3-+411234567890-True-textarea] 1"
] = {
    "saveDocumentStringAnswer": {
        "answer": {"stringValue": "+411234567890"},
        "clientMutationId": "testid",
    }
}

snapshots["test_fetch_format_validators 1"] = {
    "allFormatValidators": {
        "edges": [
            {
                "node": {
                    "errorMsg": "Not valid",
                    "name": "test name english",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "test-validator",
                }
            },
            {
                "node": {
                    "errorMsg": "Please enter a valid Email address.",
                    "name": "E-mail",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "email",
                }
            },
            {
                "node": {
                    "errorMsg": "Please enter a valid phone number.",
                    "name": "Phone number",
                    "regex": "^[\\s\\/\\.\\(\\)-]*(?:\\+|0|00)(?:[\\s\\/\\.\\(\\)-]*\\d[\\s\\/\\.\\(\\)-]*){6,20}$",
                    "slug": "phone-number",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_format_validators 2"] = {
    "allFormatValidators": {
        "edges": [
            {
                "node": {
                    "errorMsg": "Nicht valid",
                    "name": "test name deutsch",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "test-validator",
                }
            },
            {
                "node": {
                    "errorMsg": "Bitte geben Sie eine gültige E-Mail-Adresse ein.",
                    "name": "E-Mail",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "email",
                }
            },
            {
                "node": {
                    "errorMsg": "Bitte geben Sie eine gültige Telefonnummer ein.",
                    "name": "Telefonnummer",
                    "regex": "^[\\s\\/\\.\\(\\)-]*(?:\\+|0|00)(?:[\\s\\/\\.\\(\\)-]*\\d[\\s\\/\\.\\(\\)-]*){6,20}$",
                    "slug": "phone-number",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_format_validators 3"] = {
    "allFormatValidators": {
        "edges": [
            {
                "node": {
                    "errorMsg": "Not valid",
                    "name": "test name english",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "test-validator",
                }
            },
            {
                "node": {
                    "errorMsg": "Veuillez entrer une addresse e-mail valide.",
                    "name": "Courriel",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "email",
                }
            },
            {
                "node": {
                    "errorMsg": "Veuillez entrer un numéro de téléphone valide.",
                    "name": "numéro de téléphone",
                    "regex": "^[\\s\\/\\.\\(\\)-]*(?:\\+|0|00)(?:[\\s\\/\\.\\(\\)-]*\\d[\\s\\/\\.\\(\\)-]*){6,20}$",
                    "slug": "phone-number",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}

snapshots["test_fetch_format_validators 4"] = {
    "allFormatValidators": {
        "edges": [
            {
                "node": {
                    "errorMsg": "Not valid",
                    "name": "test name english",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "test-validator",
                }
            },
            {
                "node": {
                    "errorMsg": "Please enter a valid Email address.",
                    "name": "E-mail",
                    "regex": "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)",
                    "slug": "email",
                }
            },
            {
                "node": {
                    "errorMsg": "Please enter a valid phone number.",
                    "name": "Phone number",
                    "regex": "^[\\s\\/\\.\\(\\)-]*(?:\\+|0|00)(?:[\\s\\/\\.\\(\\)-]*\\d[\\s\\/\\.\\(\\)-]*){6,20}$",
                    "slug": "phone-number",
                }
            },
        ],
        "pageInfo": {
            "endCursor": "YXJyYXljb25uZWN0aW9uOjI=",
            "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
        },
        "totalCount": 3,
    }
}
