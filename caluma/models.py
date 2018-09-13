from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugModel(BaseModel):
    """Models which use a slug as primary key."""

    slug = models.SlugField(max_length=50, primary_key=True)

    def __str__(self):
        return self.slug

    class Meta:
        abstract = True
