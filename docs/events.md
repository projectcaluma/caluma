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
def send_mail_on_complete_work_item(sender, work_item, user, context, **kwargs):
    if work_item.task.slug == "slug-we-are-interested-in":
        # send notification
        pass


# It's also possible to specify a sender, which refers to a mutation class,
# analog to the `permission_for` decorators
@on(completed_work_item, sender=CompleteWorkItem)
def send_mail_on_complete_work_item_2(sender, work_item, user, context, **kwargs):
    if work_item.task.slug == "slug-we-are-interested-in":
        # send notification
        pass
```

## @on

`@on` is a customized implementation of `django.dispatch.receiver` which
takes three arguments:

1. `event` (required): Event or list of events to listen to.
2. `sender` (optional): Class of sender.
3. `raise_exception` (optional): Whether to raise exceptions inside the receivers. This is `False` by default.

## Event receiver signature

An event receiver must take `sender` as it's first argument. This is the `Mutation`, the event has been emitted from.

Other arguments that must be taken by receiver functions are described in the [table below](#list-of-emitted-events).

It is recommended to always add `**kwargs` to the receiver functions signature
in case the event sends additional arguments in the future.

## List of emitted events

| Event                     | Mutations that can emit this event                                | Arguments                                        |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------ |
| `pre_create_work_item`    | `CreateWorkItem`, `SaveWorkItem`, `StartCase`, `CompleteWorkItem` | `work_item`, `user`, `context`, `validated_data` |
| `post_create_work_item`   | `CreateWorkItem`, `SaveWorkItem`, `StartCase`, `CompleteWorkItem` | `work_item`, `user`, `context`                   |
| `pre_complete_work_item`  | `CompleteWorkItem`                                                | `work_item`, `user`, `context`                   |
| `post_complete_work_item` | `CompleteWorkItem`                                                | `work_item`, `user`, `context`                   |
| `pre_cancel_work_item`    | `CancelCase`, `CancelWorkItem`                                    | `work_item`, `user`, `context`                   |
| `post_cancel_work_item`   | `CancelCase`, `CancelWorkItem`                                    | `work_item`, `user`, `context`                   |
| `pre_skip_work_item`      | `SkipWorkItem`                                                    | `work_item`, `user`, `context`                   |
| `post_skip_work_item`     | `SkipWorkItem`                                                    | `work_item`, `user`, `context`                   |
| `pre_suspend_work_item`   | `SuspendWorkItem`                                                 | `work_item`, `user`, `context`                   |
| `post_suspend_work_item`  | `SuspendWorkItem`                                                 | `work_item`, `user`, `context`                   |
| `pre_resume_work_item`    | `ResumeWorkItem`                                                  | `work_item`, `user`, `context`                   |
| `post_resume_work_item`   | `ResumeWorkItem`                                                  | `work_item`, `user`, `context`                   |
| `pre_create_case`         | `SaveCase`, `StartCase`                                           | `case`, `user`, `context`, `validated_data`      |
| `post_create_case`        | `SaveCase`, `StartCase`                                           | `case`, `user`, `context`                        |
| `pre_complete_case`       | `CompleteWorkItem`                                                | `case`, `user`, `context`                        |
| `post_complete_case`      | `CompleteWorkItem`                                                | `case`, `user`, `context`                        |
| `pre_cancel_case`         | `CancelCase`                                                      | `case`, `user`, `context`                        |
| `post_cancel_case`        | `CancelCase`                                                      | `case`, `user`, `context`                        |
| `pre_suspend_case`        | `SuspendCase`                                                     | `case`, `user`, `context`                        |
| `post_suspend_case`       | `SuspendCase`                                                     | `case`, `user`, `context`                        |
| `pre_resume_case`         | `ResumeCase`                                                      | `case`, `user`, `context`                        |
| `post_resume_case`        | `ResumeCase`                                                      | `case`, `user`, `context`                        |

In some cases when one mutation emits multiple events, it is important to know their respective order:

- `CompleteWorkItem`:
  1. `post_complete_work_item`
  2. `post_create_work_item`
  3. `post_complete_case`

## Event receivers are blocking

For the time being, event receivers are blocking. Keep in mind that a request that leads to Caluma
emitting event(s), is not responded to before every event receiver has returned (or failed).

There are plans to provide non-blocking event receivers, so stay tuned.

## Exceptions

Exceptions in event receivers are logged, but will not affect the current db transaction.
That way, you can be sure the transaction will not be rolled-back because of an Exception in an event receiver.
However, if the `raise_exception` argument of the receiver is `True` it will raise any
exception that ocurred in the receiver function and the transaction will be rolled back.


## Event filtering

In many cases, the first thing an event handler does is to check some
conditions before continuing. For example, if you want to trigger some
side effect when a certain answer is saved, you may be tempted to write
something like this:

```python
@on(post_save, sender=models.Answer)
def set_document_family(sender, instance, **kwargs):
    if instance.question_id != 'the-relevant-question':
        return
    do_the_actual_work_here()
```
This gets cumbersome and hard to read, especially when the checks get more
complex. Caluma provides an `filter_events()` decorator that helps with this.

Here's the same example from above, but this time, using the event filter:

```python
@on(post_save, sender=models.Answer)
@filter_events(lambda instance: instance.question_id == 'the-relevant-question')
def set_document_family(sender, instance, **kwargs):
    do_the_actual_work_here()
```

Any parameter that is passed to a signal handler can also be accepted by
the predicate function, it just has to take the same name. Even multiple
parameters can be read in the same way.


## Built-in django signals

Under the hood, Caluma uses Django signals for now. If you are familiar with them, you can also listen
to them in receivers. Beware, that this could be subject to change, as the event infrastructure
is not very mature yet. But we try our best to not break with the API described above.
