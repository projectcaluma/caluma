import functools
import codecs
import sys
from caluma.schema import schema
from caluma.user.models import OIDCUser
from django.test import RequestFactory
from caluma import settings
from django.core.management.base import BaseCommand


rf = RequestFactory()


def admin_request():
    request = rf.get("/graphql")
    request.user = OIDCUser(
        "sometoken", {"sub": "admin", settings.OIDC_GROUPS_CLAIM: ["admin"]}
    )

    return request


admin_schema_executor = functools.partial(schema.execute, context=admin_request())


class Command(BaseCommand):
    help = "Execute graphql file as admin user."

    def add_arguments(self, parser):
        parser.add_argument("graphql_file", type=str)

    def handle(self, **options):
        with codecs.open(options["graphql_file"], "r", "UTF-8") as f:
            req = admin_schema_executor(f.read())
        if req.errors:
            print(req.errors)
            sys.exit(1)
        print(req.data)
