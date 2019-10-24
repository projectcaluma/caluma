# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_base_format_validators[question__format_validators1-test@example.com-True-text] 1'] = {
    'saveDocumentStringAnswer': {
        'answer': {
            'stringValue': 'test@example.com'
        },
        'clientMutationId': 'testid'
    }
}

snapshots['test_base_format_validators[question__format_validators1-test@example.com-True-textarea] 1'] = {
    'saveDocumentStringAnswer': {
        'answer': {
            'stringValue': 'test@example.com'
        },
        'clientMutationId': 'testid'
    }
}

snapshots['test_base_format_validators[question__format_validators3-+411234567890-True-text] 1'] = {
    'saveDocumentStringAnswer': {
        'answer': {
            'stringValue': '+411234567890'
        },
        'clientMutationId': 'testid'
    }
}

snapshots['test_base_format_validators[question__format_validators3-+411234567890-True-textarea] 1'] = {
    'saveDocumentStringAnswer': {
        'answer': {
            'stringValue': '+411234567890'
        },
        'clientMutationId': 'testid'
    }
}
