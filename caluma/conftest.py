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
from .caluma_logging import factories as logging_factories
from .caluma_user.models import AnonymousUser, OIDCUser
from .caluma_workflow import factories as workflow_factories
from .schema import schema

Faker.add_provider(MultilangProvider)


def register_module(module):
    for _, obj in inspect.getmembers(module):
        if isinstance(obj, FactoryMetaClass) and not obj._meta.abstract:
            register(obj)


register_module(form_factories)
register_module(logging_factories)
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

    def factory(use_table=False, use_subform=False):
        form = form_factory(slug="top_form")
        document = document_factory(form=form)

        questions = {}
        answers = {}

        questions["top_question"] = question_factory(
            slug="top_question", is_required="true", is_hidden="false"
        )

        form_question_factory(form=form, question=questions["top_question"])
        answers["top_question"] = answer_factory(
            document=document, question_id="top_question"
        )

        if use_table:
            row_form = form_factory(slug="row_form")
            questions["table_question"] = question_factory(
                type="table",
                slug="table",
                row_form=row_form,
                is_required="true",
                is_hidden="false",
            )
            form_question_factory(form=form, question=questions["table_question"])
            questions["column"] = question_factory(
                slug="column", is_required="true", is_hidden="false"
            )
            form_question_factory(form=row_form, question=questions["column"])

            answers["table_question"] = answer_factory(
                document=document, question=questions["table_question"]
            )

            row_doc = document_factory(form=row_form)
            answers["column"] = answer_factory(
                document=row_doc, question=questions["column"]
            )
            answers["table_question"].documents.add(row_doc)

        if use_subform:
            sub_form = form_factory(slug="sub_form")
            questions["form_question"] = question_factory(
                type="form",
                slug="form_question",
                sub_form=sub_form,
                is_required="true",
                is_hidden="false",
            )
            form_question_factory(form=form, question=questions["form_question"])
            questions["sub_question"] = question_factory(
                slug="sub_question", is_required="true", is_hidden="false"
            )
            form_question_factory(form=sub_form, question=questions["sub_question"])

            answers["sub_question"] = answer_factory(
                document=document, question_id="sub_question"
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
