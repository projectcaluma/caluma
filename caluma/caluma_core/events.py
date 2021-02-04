import logging
from warnings import warn

logger = logging.getLogger(__name__)


class SignalHandlingError(RuntimeError):
    def __init__(self, exceptions, *args, **kwargs):
        self.caught_exceptions = exceptions

        super().__init__(*args, **kwargs)

    def __str__(self):
        return ", ".join([str(e) for e in self.caught_exceptions])


def on(event, raise_exception=False, *args, **kwargs):
    deprecation_reason = getattr(event, "_deprecation_reason", None)

    if deprecation_reason:  # pragma: no cover
        warn(deprecation_reason, DeprecationWarning)

    def _decorator(func):
        func._raise_exception = raise_exception

        if isinstance(event, (list, tuple)):
            for e in event:
                e.connect(func, **kwargs)
        else:
            event.connect(func, **kwargs)
        return func

    return _decorator


def send_event(signal, **kwargs):
    """
    Send events and handle exceptions in receiver functions.

    This wrapper handles the sending of signals as well as handling of any
    Exceptions that occur. Exceptions are logged with `ERROR` level per
    default, but not raised, in order to prevent rollback of the transaction.
    However, if the `raise_exception` flag on the receiver is set to `True`
    it will collect those errors and raise a `SignalHandlingError` containing
    all caught exceptions.
    """
    result = signal.send_robust(**kwargs)

    caught_exceptions = []
    for func, exc in result:
        if exc is not None:
            if func._raise_exception:
                caught_exceptions.append(exc)

            logger.error(
                f'Error in event handler "{func.__module__}.{func.__name__}":',
                exc_info=exc,
            )

    if caught_exceptions:
        raise SignalHandlingError(caught_exceptions)

    return result


class SendEventSerializerMixin:
    def send_event(self, event, **kwargs):
        send_event(
            event,
            sender=self.context["mutation"],
            user=self.context["request"].user,
            context=getattr(self, "context_data", None),
            **kwargs,
        )  # noqa
