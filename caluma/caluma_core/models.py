import uuid

from django.db import models
from graphene.utils.str_converters import to_camel_case
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

    def __str__(self):
        return self.slug

    class Meta:
        abstract = True


class UUIDModel(BaseModel, HistoricalModel):
    """
    Models which use uuid as primary key.

    Defined as Caluma default
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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

    class Meta:
        abstract = True


class ChoicesCharField(models.CharField):
    """
    Choices char field type with specific form field.

    Graphene Django Filter converter uses formfield for conversion.
    To support enum choices for arguments we need to set a label
    which is unique across schema.
    """

    def formfield(self, **kwargs):
        # Postfixing newly created filter with Argument to avoid conflicts
        # with query nodes
        meta = self.model._meta
        name = to_camel_case(f"{meta.object_name}_{self.name}_argument")

        return super().formfield(label=name, **kwargs)
