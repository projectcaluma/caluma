from django.core.management.commands import migrate

from .migrate_to_prefixed_apps import Command as PrefixCommand


class Command(migrate.Command):
    """migrate command wrapper to add custom logic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _set_app_prefix(self):
        prefix_migrator = PrefixCommand()
        prefix_migrator.collect()

        if prefix_migrator.queries:  # pragma: no cover
            # this is already tested in test_migrate_to_prefixed_apps
            self.stderr.write(
                "Adding table prefix and updating django internal tables."
            )
            prefix_migrator.apply()

    def handle(self, *args, **options):
        self._set_app_prefix()

        super().handle(*args, **options)
