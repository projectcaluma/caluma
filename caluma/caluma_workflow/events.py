import sys

from django.dispatch import Signal

from caluma.caluma_core.events import send_event

module = sys.modules[__name__]

MODEL_ACTIONS = {
    "work_item": ["create", "complete", "cancel", "skip", "suspend", "resume", "redo"],
    "case": ["create", "complete", "cancel", "suspend", "resume", "reopen"],
}

# create "pre|post"_"create|complete|..."_"work_item|case" events in all given combinations
for obj, actions in MODEL_ACTIONS.items():
    for action in actions:
        for prefix in ["pre", "post"]:

            setattr(module, f"{prefix}_{action}_{obj}", Signal())

# TODO: remove in the next major release since those are events are deprecated...
# ... in favor of "post_" events
created_work_item = Signal()
completed_work_item = Signal()
skipped_work_item = Signal()
suspended_work_item = Signal()
resumed_work_item = Signal()
completed_case = Signal()
created_case = Signal()
suspended_case = Signal()
resumed_case = Signal()

# ... also in favor of the american notation
canceled_work_item = Signal()
cancelled_work_item = Signal()
canceled_case = Signal()
cancelled_case = Signal()

DEPRECATIONS = {
    "post_create_work_item": ["created_work_item"],
    "post_complete_work_item": ["completed_work_item"],
    "post_cancel_work_item": ["canceled_work_item", "cancelled_work_item"],
    "post_skip_work_item": ["skipped_work_item"],
    "post_suspend_work_item": ["suspended_work_item"],
    "post_resume_work_item": ["resumed_work_item"],
    "post_complete_case": ["completed_case"],
    "post_cancel_case": ["canceled_case", "cancelled_case"],
    "post_create_case": ["created_case"],
    "post_suspend_case": ["suspended_case"],
    "post_resume_case": ["resumed_case"],
}

for new, deprecations in DEPRECATIONS.items():
    for old in deprecations:
        getattr(
            module, old
        )._deprecation_reason = f"`caluma_workflow.events.{old}` is deprecated in favor of `caluma_workflow.events.{new}` and will be removed in the next major version."


# TODO remove this in next major release and replace call sites with regular send_event
def send_event_with_deprecations(event_name, **kwargs):
    new_event = getattr(module, event_name)
    send_event(new_event, **kwargs)

    if event_name not in DEPRECATIONS:
        return

    for deprecation in DEPRECATIONS[event_name]:
        old_event = getattr(module, deprecation)
        send_event(old_event, **kwargs)
