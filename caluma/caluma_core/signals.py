from django.db.models.signals import pre_save
from django.dispatch import receiver

from caluma.caluma_core.events import filter_events
from caluma.caluma_core.models import PathModelMixin


@receiver(pre_save)
@filter_events(lambda sender: PathModelMixin in sender.mro())
def store_path(sender, instance, **kwargs):
    """Store/update the path of the object.

    Note: Due to the fact that this structure is relatively rigid,
    we don't update our children. For one, they may be difficult to
    collect, but also, the parent-child relationship is not expected
    to change, and structures are built top-down, so any object
    is expected to exist before it's children come into play.
    """
    instance.path = instance.calculate_path()
