import hashlib
import json
from collections import defaultdict

from django.core.management.base import BaseCommand

from caluma.caluma_analytics.models import AnalyticsTable
from caluma.caluma_analytics.simple_table import SimpleTable


class Command(BaseCommand):
    help = "Run an analytics table and show it's output"

    def add_arguments(self, parser):
        parser.add_argument("id", nargs="*", help="Identifier of the analytics table")
        parser.add_argument(
            "--json", action="store_true", help="Request output in JSON format"
        )
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Instead of outputting the analysis, show the SQL",
        )
        parser.add_argument(
            "--sqlonly",
            action="store_true",
            help="Only output SQL, do not run the analysis",
        )

    def show_existing_tables(self):
        print("No analytics table specified. The following tables are available:")
        print("  ID:                  NAME:")
        for table in AnalyticsTable.objects.all():
            print(f"  {table.slug:20} {table.name}")

    def handle(self, **options):
        if not len(options["id"]):
            return self.show_existing_tables()

        analytics_table = AnalyticsTable.objects.get(pk__in=options["id"])
        table = SimpleTable(analytics_table)

        if options["sqlonly"]:
            self.show_sql(table)
            return
        if options["sql"]:
            self.show_sql(table)

        try:
            records = table.get_records()

            if not records:  # pragma: no cover
                return

            if options["json"]:
                self.show_json(records)
            else:
                self.show_table(records)
        except (BrokenPipeError, KeyboardInterrupt):  # pragma: no cover
            # if user presses Ctrl+C, or runs output into
            # a pipe and stops that, we don't bother telling
            # them what happened
            pass

    def show_sql(self, table):
        # Writing SQL dump to STDERR, so users can still
        # split/pipe data output to somewhere else
        sql, params = table.get_sql_and_params()
        self.stderr.write("-- SQL: \n")
        self.stderr.write(sql)
        self.stderr.write("-- PARAMS: \n")
        for name, val in params.items():
            self.stderr.write(f"--     {name}: {val}\n")
        self.stderr.flush()

    def show_json(self, records):
        print(
            json.dumps(
                [{k: str(v) for k, v in rec.items()} for rec in records], indent=4
            )
        )

    def show_table(self, records):
        """Output the analytics table as an ASCII table to the console."""

        def _rowkey(val):
            # rowkey is used so any column names (aliases) incompatible
            # with format string syntax won't trip up the output code
            return "row" + hashlib.md5(val.encode("utf-8")).hexdigest()

        col_lengths = defaultdict(int)

        for rec in records:
            for alias, val in rec.items():
                key = _rowkey(alias)
                new_len = max(col_lengths[key], len(str(val)), len(alias))
                col_lengths[key] = new_len

        # just use the last record to get the labels
        col_labels = {_rowkey(k): k for k in rec.keys()}

        format_string = " ".join(
            [
                "{" + col + ":<" + str(length + 2) + "}"
                for col, length in col_lengths.items()
            ]
        )
        print(format_string.format(**col_labels))
        print(
            format_string.format(
                **{col: "-" * length for col, length in col_lengths.items()}
            )
        )

        for rec in records:
            fdata = {_rowkey(k): str(v) for k, v in rec.items()}
            print(format_string.format(**fdata))
