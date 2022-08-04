import contextlib
import datetime
import functools
import inspect
import sys

import pytest
import urllib3
from django.apps import apps
from django.core.cache import cache
from factory import Faker
from factory.base import FactoryMetaClass
from graphene import ResolveInfo
from minio import Minio
from minio.datatypes import Object as MinioStatObject
from pytest_factoryboy import register
from pytest_factoryboy.fixture import Box

from .caluma_analytics import factories as analytics_factories
from .caluma_core.faker import MultilangProvider
from .caluma_core.models import HistoricalRecords
from .caluma_form import factories as form_factories
from .caluma_logging import factories as logging_factories
from .caluma_user.models import AnonymousUser, OIDCUser
from .caluma_workflow import factories as workflow_factories
from .schema import schema

Faker.add_provider(MultilangProvider)


def register_module(module):
    # We need to pass the locals of this file to the register method to make
    # sure they are injected on the conftest locals instead of the default
    # locals which would be the locals of this function
    conftest_locals = Box(sys._getframe(1).f_locals)

    for _, obj in inspect.getmembers(module):
        if isinstance(obj, FactoryMetaClass) and not obj._meta.abstract:
            register(obj, _caller_locals=conftest_locals)


register_module(form_factories)
register_module(logging_factories)
register_module(workflow_factories)
register_module(analytics_factories)


@pytest.fixture(scope="function", autouse=True)
def _autoclear_cache():
    cache.clear()


@pytest.fixture
def admin_groups():
    return ["admin"]


@pytest.fixture
def admin_user(settings, admin_groups):
    return OIDCUser(
        b"sometoken", {"sub": "admin", settings.OIDC_GROUPS_CLAIM: admin_groups}
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
        None,
        None,
        None,
        None,
        None,
        None,
        context=anonymous_request,
        # TODO: see if this has an influence on execution, might need parametrization
        is_awaitable=lambda x: False,
    )


@pytest.fixture
def admin_info(admin_request):
    """Mock for GraphQL resolve info embedding authenticated django request as context."""
    return ResolveInfo(
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        context=admin_request,
        # TODO: see if this has an influence on execution, might need parametrization
        is_awaitable=lambda x: False,
    )


def simple_history_middleware(next, root, info, **args):
    """Mimick behaviour of simple_history.middleware.HistoryRequestMiddleware."""
    HistoricalRecords.thread.request = info.context
    return next(root, info, **args)


@pytest.fixture
def schema_executor(anonymous_request):
    return functools.partial(
        schema.execute,
        context_value=anonymous_request,
        middleware=[simple_history_middleware],
    )


@pytest.fixture
def admin_schema_executor(admin_request):
    return functools.partial(
        schema.execute,
        context_value=admin_request,
        middleware=[simple_history_middleware],
    )


@pytest.fixture
def minio_mock(mocker):
    def side_effect(bucket, object_name, expires):
        return f"http://minio/download-url/{object_name}"

    stat_response = MinioStatObject(
        # taken from a real-world minio stat() call
        bucket_name="caluma-media",
        object_name="a3d0429d-5400-47ac-9d02-124592302631_attack.wav",
        etag="5d41402abc4b2a76b9719d911017c592",
        size=8200,
        last_modified=datetime.datetime(
            2021, 3, 5, 15, 24, 33, tzinfo=datetime.timezone.utc
        ),
        content_type="application/pdf",
        metadata=urllib3._collections.HTTPHeaderDict(
            {
                "Accept-Ranges": "bytes",
                "Content-Length": "5",
                "Content-Security-Policy": "block-all-mixed-content",
                "Content-Type": "binary/octet-stream",
                "ETag": '"5d41402abc4b2a76b9719d911017c592"',
                "Last-Modified": "Fri, 05 Mar 2021 15:24:33 GMT",
                "Server": "MinIO",
                "Vary": "Origin",
                "X-Amz-Request-Id": "16697BAAD69D2214",
                "X-Xss-Protection": "1; mode=block",
                "Date": "Fri, 05 Mar 2021 15:25:15 GMT",
            }
        ),
        owner_id=None,
        owner_name=None,
        storage_class=None,
        version_id=None,
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


@pytest.fixture
def form_and_document(
    db,
    form_factory,
    question_factory,
    form_question_factory,
    document_factory,
    answer_factory,
):
    """
    Return a factory for a form and document.

    The return value is a 4-tuple with the following values:
        (form, document, questions_dict, answers_dict)

    Optionally add a table question (and a row in the document),
    and a subform for added complexity.

    You can call the factory multiple times, in which case the
    created forms will be the same, but new document structures
    will be returned each time.

    The slugs are named as follows:

    * form: top_form
       * question: top_question
       * question: table
           * row_form: row_form
               * question: column
       * question: form_question
           * sub_form: sub_form
               * question: sub_question
    """

    def fallback_factory(factory, **kwargs):
        existing = factory._meta.model.objects.filter(**kwargs).first()
        if existing:
            return existing
        return factory(**kwargs)

    def factory(use_table=False, use_subform=False):
        form = fallback_factory(
            form_factory, slug="top_form", meta={"is-top-form": True, "level": 0}
        )
        document = document_factory(form=form)

        questions = {}
        answers = {}

        questions["top_question"] = fallback_factory(
            question_factory,
            slug="top_question",
            type="text",
            is_required="true",
            is_hidden="false",
        )

        fallback_factory(
            form_question_factory, form=form, question=questions["top_question"]
        )
        answers["top_question"] = answer_factory(
            document=document, question=questions["top_question"]
        )

        if use_table:
            row_form = fallback_factory(form_factory, slug="row_form")
            questions["table"] = fallback_factory(
                question_factory,
                type="table",
                slug="table",
                row_form=row_form,
                is_required="true",
                is_hidden="false",
            )
            fallback_factory(
                form_question_factory, form=form, question=questions["table"]
            )
            questions["column"] = fallback_factory(
                question_factory,
                type="float",
                slug="column",
                is_required="true",
                is_hidden="false",
            )
            fallback_factory(
                form_question_factory, form=row_form, question=questions["column"]
            )

            answers["table"] = answer_factory(
                document=document, question=questions["table"]
            )

            row_doc = document_factory(form=row_form, family=document)
            answers["column"] = answer_factory(
                document=row_doc, question=questions["column"]
            )
            answers["table"].documents.add(row_doc)

        if use_subform:
            sub_form = fallback_factory(
                form_factory, slug="sub_form", meta={"is-top-form": False, "level": 1}
            )
            questions["form"] = fallback_factory(
                question_factory,
                type="form",
                slug="form",
                sub_form=sub_form,
                is_required="true",
                is_hidden="false",
            )
            fallback_factory(
                form_question_factory, form=form, question=questions["form"]
            )
            questions["sub_question"] = fallback_factory(
                question_factory,
                slug="sub_question",
                type="integer",
                is_required="true",
                is_hidden="false",
            )
            fallback_factory(
                form_question_factory, form=sub_form, question=questions["sub_question"]
            )

            answers["sub_question"] = answer_factory(
                document=document, question=questions["sub_question"]
            )

        return (form, document, questions, answers)

    return factory


@pytest.fixture
def sorted_snapshot(snapshot):
    """Return a sortable snapshot that sorts a list in a nested data structure.

    The first arg (name) denotes the key/variable in the data structure which holds sortable list.
    The second arg (key) is passed to the builtin `sorted` function.
    """

    def _sorted(name, key=None):
        def _(data, path):
            if isinstance(data, list) and path[-1][0] == name:
                return sorted(data, key=key)
            return data

        return _

    def custom_snapshot(*args):
        return snapshot(matcher=_sorted(*args))

    return custom_snapshot


@pytest.fixture
def set_date(freezer):
    """Run a block of code at a certain date (context manager).

    Uses freezegun, but allows you to override the frozen date.

    Provides a context manager, where everything within the "with"
    block is run at the given date:

    >>> @pytest.mark.freeze_time('2022-02-22')
    >>> def test_foo(set_date):
            assert datetime.now() == datetime(2022,2,22)

            with set_date('2022-01-01'):
                assert datetime.now() == datetime(2022,1,1)

            assert datetime.now() == datetime(2022,2,22)
    """

    @contextlib.contextmanager
    def make_context(date):
        old_now = datetime.datetime.now()
        freezer.move_to(date)
        yield
        freezer.move_to(old_now)

    return make_context
