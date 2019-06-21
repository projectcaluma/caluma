import uuid

from django.conf import settings
from django.db import models

from simple_history.models import HistoricalRecords


def _history_user_getter(historical_instance):
    return historical_instance.history_user_id


def _history_user_setter(historical_instance, user):
    request = getattr(HistoricalRecords.thread, "request", None)
    if request is not None:
        historical_instance.history_user_id = request.user.username
    else:
        historical_instance.history_user_id = None


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by_user = models.CharField(max_length=150, blank=True, null=True)
    created_by_group = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
    )
    if settings.SIMPLE_HISTORY_ACTIVE:
        history = HistoricalRecords(
            inherit=True,
            history_user_id_field=models.CharField(null=True, max_length=150),
            history_user_setter=_history_user_setter,
            history_user_getter=_history_user_getter,
        )

    class Meta:
        abstract = True


class SlugModel(BaseModel):
    """
    Models which use a slug as primary key.

    Defined as Caluma default for configuration so it is possible
    to merge between developer and user configuration.
    """

    slug = models.SlugField(max_length=50, primary_key=True)

    def __str__(self):
        return self.slug

    class Meta:
        abstract = True


class UUIDModel(BaseModel):
    """
    Models which use uuid as primary key.

    Defined as Caluma default
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class NaturalKeyModel(BaseModel):
    """Models which use a natural key as primary key."""

    id = models.CharField(max_length=255, unique=True, primary_key=True)

    def natural_key(self):  # pragma: no cover
        raise NotImplementedError()

    def save(self, *args, **kwargs):
        self.id = self.natural_key()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
