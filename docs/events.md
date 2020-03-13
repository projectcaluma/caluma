# Caluma Events

Caluma emits events at certain stages of a workflow. These can be used to implement own "side-effects".

In contrast to the `validations` extension, events are emitted AFTER a certain event happened.

## Configuration

To configure a module where event receivers should be imported from, you can set the `EVENT_RECEIVER_MODULES` environment variable.

When using the Caluma service, you can place your receivers in `caluma.extensions.events` and set `EVENT_RECEIVER_MODULES` to
`["caluma.extensions.events"]`.

## Example event receiver

```python
from caluma.caluma_core.events import on
from caluma.caluma_workflow.events import completed_work_item
from caluma.caluma_workflow.schema import CompleteWorkItem


@on(completed_work_item)
def send_mail_on_complete_work_item(sender, work_item, **kwargs):
    if work_item.task.slug == "slug-we-are-interested-in":
        # send notification
        pass


# It's also possible to specify a sender, which refers to a mutation class,
# analog to the `permission_for` decorators
@on(completed_work_item, sender=CompleteWorkItem)
def send_mail_on_complete_work_item_2(sender, work_item, **kwargs):
    if work_item.task.slug == "slug-we-are-interested-in":
        # send notification
        pass
```

## @on

Right now `@on` is just an alias for `django.dispatch.receiver`. This very likely will change
in the future, but the public API should stay the same.

The `@on` decorator takes two arguments:

1. `event` (required): Event or list of events to listen to.
2. `sender` (optional): Class of sender.

## Event receiver signature

An event receiver must take `sender` as it's first argument. This is the `Mutation`, the event has been emitted from.

Other arguments that must be taken by receiver functions are described in the [table below](#list-of-emitted-events).

It is recommended to always add `**kwargs` to the receiver functions signature
in case the event sends additional arguments in the future.

## List of emitted events

| Event                    | Mutations that can emit this event                                | Arguments    |
| ------------------------ | ----------------------------------------------------------------- | ------------ |
|  `created_work_item`     | `CreateWorkItem`, `SaveWorkItem`, `StartCase`, `CompleteWorkItem` | `work_item`  |
|  `completed_work_item`   | `CompleteWorkItem`                                                | `work_item`  |
|  `cancelled_work_item`   | `CancelCase`                                                      | `work_item`  |
|  `skipped_work_item`     | `SkipWorkItem`                                                    | `work_item`  |
|  `created_case`          | `SaveCase`, `StartCase`                                           | `case`       |
|  `completed_case`        | `CompleteWorkItem`                                                | `case`       |
|  `cancelled_case`        | `CancelCase`                                                      | `case`       |

## Event receivers are blocking

For the time being, event receivers are blocking. Keep in mind that a request that leads to Caluma
emitting event(s), is not responded to before every event receiver has returned (or failed).

There are plans to provide non-blocking event receivers, so stay tuned.

## Exceptions

Exceptions in event receivers are logged, but will not affect the current db transaction.
That way, you can be sure the transaction will not be rolled-back because of an Exception in an event receiver.


## Built-in django signals

Under the hood, Caluma uses Django signals for now. If you are familiar with them, you can also listen
to them in receivers. Beware, that this could be subject to change, as the event infrastructure
is not very mature yet. But we try our best to not break with the API described above.
