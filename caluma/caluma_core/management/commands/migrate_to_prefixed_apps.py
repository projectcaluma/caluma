from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import ProgrammingError


class Command(BaseCommand):
    """Migrate db to prefixed apps."""

    help = "Migrate db to prefixed apps."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.revert = False
        self.queries = []
        self.prefix = "caluma_"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--force", action="store_true", help="Do the migration"
        )
        parser.add_argument(
            "-r", "--revert", action="store_true", help="Revert the migration"
        )

    @property
    def _act_prefix(self):
        prefix = ""
        if self.revert:
            prefix = self.prefix
        return prefix

    def _migration_needed(self):
        query = f"""SELECT "app" FROM "django_migrations" WHERE "app" = '{self._act_prefix}form';"""
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
            except ProgrammingError as e:  # pragma: no cover
                # happens only on initial migration for new project
                if e.args[0].startswith('relation "django_migrations" does not exist'):
                    return False
                raise
            if cursor.fetchone():
                return True
        return False

    def _get_table_list(self):
        query = f"""SELECT tablename FROM pg_catalog.pg_tables WHERE tablename LIKE '{self._act_prefix}form_%' OR tablename LIKE '{self._act_prefix}workflow_%';"""
        with connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def _collect_content_type_queries(self):
        queries = [
            f"""UPDATE django_content_type SET app_label = CONCAT('{self.prefix}', app_label) WHERE app_label = 'form' OR app_label = 'workflow';"""
        ]
        if self.revert:
            queries = [
                """UPDATE django_content_type SET app_label = REPLACE(app_label, 'caluma_', '');"""
            ]
        return queries

    def _collect_django_migrations_queries(self):
        queries = [
            f"""UPDATE django_migrations SET app = CONCAT('{self.prefix}', app) WHERE app = 'form' OR app = 'workflow';"""
        ]
        if self.revert:
            queries = [
                """UPDATE django_migrations SET app = REPLACE(app, 'caluma_', '');"""
            ]
        return queries

    def _collect_prefix_tables_queries(self, tables: list):
        queries = []
        for table in tables:
            query = f"""ALTER TABLE {table} RENAME TO {self.prefix}{table};"""
            if self.revert:
                query = f"""ALTER TABLE {table} RENAME TO {table.replace(self.prefix, '')};"""
            queries.append(query)
        return queries

    def collect(self):
        if not self._migration_needed():
            return
        self.queries += self._collect_content_type_queries()
        self.queries += self._collect_django_migrations_queries()
        tables = self._get_table_list()
        self.queries += self._collect_prefix_tables_queries(tables)
        return self.queries

    def apply(self):
        with connection.cursor() as cursor:
            for query in self.queries:
                cursor.execute(query)

    def handle(self, *args, **options):
        if options["revert"]:
            self.revert = True

        self.collect()

        if not self.queries:
            self.stderr.write("Seems the DB is already in the desired state!")
            return

        self.stderr.write("\n".join(self.queries))

        if options["force"]:
            self.apply()
