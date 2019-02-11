import functools
import inspect

import pytest
from django.core.cache import cache
from factory import Faker
from factory.base import FactoryMetaClass
from graphene import ResolveInfo
from pytest_factoryboy import register

from .core.faker import MultilangProvider
from .form import factories as form_factories
from .schema import schema
from .user.models import AnonymousUser, OIDCUser
from .workflow import factories as workflow_factories

Faker.add_provider(MultilangProvider)


def register_module(module):
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, FactoryMetaClass) and not obj._meta.abstract:
            register(obj)


register_module(form_factories)
register_module(workflow_factories)


@pytest.fixture(scope="function", autouse=True)
def _autoclear_cache():
    cache.clear()


@pytest.fixture
def admin_groups():
    return ["admin"]


@pytest.fixture
def admin_user(settings, admin_groups):
    return OIDCUser(
        "sometoken", {"sub": "admin", settings.OIDC_GROUPS_CLAIM: admin_groups}
    )


@pytest.fixture
def admin_request(rf, admin_user):
    request = rf.get("/graphql")
    request.user = admin_user
    return request


@pytest.fixture
def anonymous_request(rf):
    request = rf.get("/graphql")
    request.user = AnonymousUser()
    return request


@pytest.fixture
def info(anonymous_request):
    """Mock for GraphQL resolve info embedding django request as context."""
    return ResolveInfo(
        None,
        None,
        None,
        None,
        schema=None,
        fragments=None,
        root_value=None,
        operation=None,
        variable_values=None,
        context=anonymous_request,
    )


@pytest.fixture
def admin_info(admin_request):
    """Mock for GraphQL resolve info embedding authenticated django request as context."""
    return ResolveInfo(
        None,
        None,
        None,
        None,
        schema=None,
        fragments=None,
        root_value=None,
        operation=None,
        variable_values=None,
        context=admin_request,
    )


@pytest.fixture
def schema_executor(anonymous_request):
    return functools.partial(schema.execute, context=anonymous_request)


@pytest.fixture
def admin_schema_executor(admin_request):
    return functools.partial(schema.execute, context=admin_request)
