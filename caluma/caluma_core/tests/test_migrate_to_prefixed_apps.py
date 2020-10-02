import os

import pytest
from django.core.management import call_command
from django.db import connection


@pytest.mark.parametrize("force", [True, False])
def test_migrate_to_prefixed_apps(db, force):
    def _is_applied(query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            if cursor.fetchone():
                return True
        return False

    def changes_applied():
        applied = (
            _is_applied(
                """SELECT "app_label" FROM "django_content_type" WHERE "app_label" = 'caluma_form';"""
            ),
            _is_applied(
                """SELECT "app" FROM "django_migrations" WHERE "app" = 'caluma_form';"""
            ),
            _is_applied(
                """SELECT tablename FROM pg_catalog.pg_tables WHERE tablename LIKE 'caluma_form_%' OR tablename LIKE 'caluma_workflow_%';"""
            ),
            _is_applied(
                """SELECT sequence_name FROM information_schema.sequences WHERE sequence_name LIKE 'caluma_form_%' OR sequence_name LIKE 'caluma_workflow_%';"""
            ),
        )
        if all(applied):
            return True
        elif not any(applied):
            return False
        else:  # pragma: no cover
            raise Exception("DB is in a state it should never be!")

    kwargs = {}
    if force:
        kwargs["force"] = force

    assert changes_applied()

    call_command(
        "migrate_to_prefixed_apps", **kwargs, revert=True, stderr=open(os.devnull, "w")
    )

    if force:
        assert not changes_applied()
    else:
        assert changes_applied()

    call_command("migrate_to_prefixed_apps", **kwargs, stderr=open(os.devnull, "w"))

    assert changes_applied()
