import uuid_extensions
from django.apps import apps
from django.db import models
from simple_history.models import HistoricalRecords, registered_models


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


class ProxyAwareHistoricalRecords(HistoricalRecords):
    """Historical records with shared history for proxy models.

    This is a workaround for https://github.com/jazzband/django-simple-history/issues/544.

    Copied from https://github.com/jazzband/django-simple-history/issues/544#issuecomment-1538615799
    """

    def _find_base_history(self, opts):
        base_history = None
        for parent_class in opts.parents.keys():
            if hasattr(parent_class, "history"):
                base_history = parent_class.history.model
        return base_history

    def create_history_model(self, model, inherited):
        opts = model._meta
        if opts.proxy:
            base_history = self._find_base_history(opts)
            if base_history:
                return self.create_proxy_history_model(model, inherited, base_history)

        return super().create_history_model(model, inherited)

    def create_proxy_history_model(self, model, inherited, base_history):
        opts = model._meta
        attrs = {
            "__module__": self.module,
            "_history_excluded_fields": self.excluded_fields,
        }
        app_module = f"{opts.app_label}.models"
        if inherited:
            attrs["__module__"] = model.__module__
        elif model.__module__ != self.module:  # pragma: no cover
            # registered under different app
            attrs["__module__"] = self.module
        elif app_module != self.module:  # pragma: no cover
            # Abuse an internal API because the app registry is loading.
            app = apps.app_configs[opts.app_label]
            models_module = app.name
            attrs["__module__"] = models_module

        attrs.update(
            Meta=type("Meta", (), {**self.get_meta_options(model), "proxy": True})
        )
        if self.table_name is not None:  # pragma: no cover
            attrs["Meta"].db_table = self.table_name

        name = self.get_history_model_name(model)
        registered_models[opts.db_table] = model
        return type(str(name), (base_history,), attrs)


class HistoricalModel(models.Model):
    history = ProxyAwareHistoricalRecords(
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
