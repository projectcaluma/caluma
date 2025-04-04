import uuid_extensions
from django.db import models
from simple_history.models import HistoricalRecords


def _history_user_getter(historical_instance):
    return historical_instance.history_user_id


def _history_user_setter(historical_instance, user):
    request = getattr(HistoricalRecords.thread, "request", None)
    user = None
    if request is not None:
        user = request.user.username
        if request.user.__class__.__name__ == "AnonymousUser":
            user = "AnonymousUser"
    historical_instance.history_user_id = user


class HistoricalModel(models.Model):
    history = HistoricalRecords(
        inherit=True,
        history_user_id_field=models.CharField(null=True, max_length=150),
        history_user_setter=_history_user_setter,
        history_user_getter=_history_user_getter,
    )

    class Meta:
        abstract = True


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)
    created_by_user = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
    )
    created_by_group = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
    )
    modified_by_user = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
    )
    modified_by_group = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
    )

    def __str__(self):
        return str(self.pk)

    class Meta:
        abstract = True


class SlugModel(BaseModel, HistoricalModel):
    """
    Models which use a slug as primary key.

    Defined as Caluma default for configuration so it is possible
    to merge between developer and user configuration.
    """

    # Slug is limited to 127 chars to enable the NaturalKeyModel
    # (see below) to reference two slugs, separated with a dot.
    slug = models.SlugField(max_length=127, primary_key=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(slug={self.slug})"

    class Meta:
        abstract = True


class UUIDModel(BaseModel, HistoricalModel):
    """
    Models which use uuid as primary key.

    Defined as Caluma default
    """

    id = models.UUIDField(
        primary_key=True, default=uuid_extensions.uuid7, editable=False
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    class Meta:
        abstract = True


class NaturalKeyModel(BaseModel, HistoricalModel):
    """Models which use a natural key as primary key."""

    id = models.CharField(max_length=255, unique=True, primary_key=True)

    def natural_key(self):  # pragma: no cover
        raise NotImplementedError()

    def save(self, *args, **kwargs):
        self.id = self.natural_key()
        return super().save(*args, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    class Meta:
        abstract = True


class ChoicesCharField(models.CharField):
    # This is only needed for backwards compatibility in the migrations
    pass
