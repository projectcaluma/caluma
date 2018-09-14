import inspect

import pytest
from factory import Faker
from factory.base import FactoryMetaClass
from graphql.error import format_error
from pytest_factoryboy import register
from snapshottest.pytest import PyTestSnapshotTest

from .document import factories as document_factories
from .faker import MultilangProvider
from .form import factories as form_factories
from .workflow import factories as workflow_factories

Faker.add_provider(MultilangProvider)


def register_module(module):
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, FactoryMetaClass) and not obj._meta.abstract:
            register(obj)


register_module(form_factories)
register_module(document_factories)
register_module(workflow_factories)


@pytest.fixture
def snapshot(request):
    class GraphQlSnapshotTest(PyTestSnapshotTest):
        def assert_execution_result(self, result):
            self.assert_match(
                {
                    "data": result.data,
                    "errors": [format_error(e) for e in result.errors or []],
                }
            )

    with GraphQlSnapshotTest(request) as snapshot_test:
        yield snapshot_test
