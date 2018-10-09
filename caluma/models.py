import uuid

from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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
