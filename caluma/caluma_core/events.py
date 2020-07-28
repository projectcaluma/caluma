import logging

from django.dispatch import receiver as on  # noqa

logger = logging.getLogger(__name__)


def send_event(signal, **kwargs):
    """
    Send events and handle exceptions in receiver functions.

    This wrapper handles the sending of signals as well as handling of any Exceptions that
    occur. Exceptions are logged with `ERROR` level, but not raised, in order to prevent
    rollback of the transaction.
    """
    result = signal.send_robust(**kwargs)
    for func, exc in result:
        if exc is not None:
            logger.error(
                f'Error in event handler "{func.__module__}.{func.__name__}":',
                exc_info=exc,
            )
    return result


class SendEventSerializerMixin:
    def send_event(self, event, **kwargs):
        send_event(
            event,
            sender=self.context["mutation"],
            user=self.context["request"].user,
            **kwargs,
        )  # noqa
