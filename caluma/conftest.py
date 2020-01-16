import functools
import inspect
import time

import pytest
from django.apps import apps
from django.core.cache import cache
from factory import Faker
from factory.base import FactoryMetaClass
from graphene import ResolveInfo
from minio import Minio
from minio.definitions import Object as MinioStatObject
from pytest_factoryboy import register

from .caluma_core.faker import MultilangProvider
from .caluma_core.models import HistoricalRecords
from .caluma_form import factories as form_factories
from .caluma_user.models import AnonymousUser, OIDCUser
from .caluma_workflow import factories as workflow_factories
from .schema import schema

Faker.add_provider(MultilangProvider)


def register_module(module):
    for _, obj in inspect.getmembers(module):
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


def simple_history_middleware(next, root, info, **args):
    """Mimick behaviour of simple_history.middleware.HistoryRequestMiddleware."""
    HistoricalRecords.thread.request = info.context
    return next(root, info, **args)


@pytest.fixture
def schema_executor(anonymous_request):
    return functools.partial(
        schema.execute,
        context=anonymous_request,
        middleware=[simple_history_middleware],
    )


@pytest.fixture
def admin_schema_executor(admin_request):
    return functools.partial(
        schema.execute, context=admin_request, middleware=[simple_history_middleware]
    )


@pytest.fixture
def minio_mock(mocker):
    def side_effect(bucket, object_name, expires):
        return f"http://minio/download-url/{object_name}"

    stat_response = MinioStatObject(
        "caluma-media",
        "some-file.pdf",
        time.struct_time((2019, 4, 5, 7, 0, 49, 4, 95, 0)),
        "0c81da684e6aaef48e8f3113e5b8769b",
        8200,
        content_type="application/pdf",
        is_dir=False,
        metadata={"X-Amz-Meta-Testtag": "super_file"},
    )
    mocker.patch.object(Minio, "presigned_get_object")
    mocker.patch.object(Minio, "presigned_put_object")
    mocker.patch.object(Minio, "stat_object")
    mocker.patch.object(Minio, "bucket_exists")
    mocker.patch.object(Minio, "make_bucket")
    mocker.patch.object(Minio, "remove_object")
    mocker.patch.object(Minio, "copy_object")
    Minio.presigned_get_object.side_effect = side_effect
    Minio.presigned_put_object.return_value = "http://minio/upload-url"
    Minio.stat_object.return_value = stat_response
    Minio.bucket_exists.return_value = True
    return Minio


@pytest.fixture
def data_source_settings(settings):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource"
    ]


@pytest.fixture
def history_mock(mocker):
    mocker.patch.object(HistoricalRecords, "create_historical_record")


@pytest.fixture
def simple_case(case_factory, document_factory, question_factory, answer_factory):
    question = question_factory()
    document = document_factory()
    answer_factory(document=document, question=question)
    case = case_factory(document=document)

    return case


@pytest.fixture
def permission_classes(settings):
    # TODO: replicate this for other globally-configured class lists
    # such as VISIBILITY_CLASSES and VALIDATION_CLASSES
    config = apps.get_app_config("caluma_core")

    old_permissions = settings.PERMISSION_CLASSES

    def set_permission_classes(class_names):
        settings.PERMISSION_CLASSES = class_names
        config.ready()

    yield set_permission_classes
    settings.PERMISSION_CLASSES = old_permissions
    config.ready()
