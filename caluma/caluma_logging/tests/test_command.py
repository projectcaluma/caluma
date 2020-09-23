from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from caluma.caluma_logging.models import AccessLog


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize(
    "keep,exist",
    [
        (None, 10),
        ("2 weeks", 10),
        ("1 month", 10),
        ("1 day", 1),
        ("7 days", 7),
        ("0 days", 0),
    ],
)
def test_cleanup_access_log(db, access_log_factory, force, keep, exist):
    for i in range(10):
        entry = access_log_factory()
        entry.timestamp = timezone.now() - timedelta(days=i)
        entry.save()

    kwargs = {"force": force}
    if keep:
        kwargs["keep"] = keep

    call_command("cleanup_access_log", **kwargs)

    count = AccessLog.objects.all().count()

    if force:
        assert count == exist
    else:
        count == 10
