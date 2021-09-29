import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.utils import ProgrammingError
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    class Meta:
        abstract = True


class PathModelMixin(models.Model):
    """
    Mixin that stores a path to the object.

    The path attribute is used for analytics and allows direct access
    and faster SELECTs.

    To you use this mixin, you must define  a property named `path_parent_attrs`
    on the model class. It's supposed to be a list of strings that contain the
    attributes to check. The first attribute that exists will be used.
    This way, you can define multiple possible parents (in a document, for example
    you can first check if it's attached to a case, or a work item, then a document family)
    """

    path = ArrayField(
        models.CharField(max_length=150),
        default=list,
        help_text="Stores a path to the given object",
    )

    def calculate_path(self, _seen_keys=None):
        if not _seen_keys:
            _seen_keys = set()
        self_pk_list = [str(self.pk)]
        if str(self.pk) in _seen_keys:
            # Not recursing any more. Root elements *may* point
            # to themselves in certain circumstances
            return []

        path_parent_attrs = getattr(self, "path_parent_attrs", None)

        if not isinstance(path_parent_attrs, list):
            raise ProgrammingError(  # pragma: no cover
                "If you use the PathModelMixin, you must define "
                "`path_parent_attrs` on the model (a list of "
                "strings that contains the attributes to check)"
            )

        for attr in path_parent_attrs:
            parent = getattr(self, attr, None)
            if parent:
                parent_path = parent.calculate_path(set([*self_pk_list, *_seen_keys]))
                if parent_path:
                    return parent_path + self_pk_list

                # Else case: If parent returns an empty list (loop case), we may
                # be in the wrong parent attribute. We continue checking the other
                # attributes (if any). If we don't find any other parents that work,
                # we'll just return as if we're the root object.

        return self_pk_list

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
