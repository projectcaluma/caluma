import uuid

from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by_user = models.CharField(max_length=150, blank=True, null=True)
    created_by_group = models.CharField(
        max_length=150, blank=True, null=True, db_index=True
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
