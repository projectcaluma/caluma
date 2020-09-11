import sys

from django.dispatch import Signal

from caluma.caluma_core.events import send_event

module = sys.modules[__name__]

MODEL_ACTIONS = {
    "work_item": ["create", "complete", "cancel", "skip", "suspend", "resume"],
    "case": ["create", "complete", "cancel", "suspend", "resume"],
}

# create "pre|post"_"create|complete|..."_"work_item|case" events in all given combinations
for obj, actions in MODEL_ACTIONS.items():
    for action in actions:
        for prefix in ["pre", "post"]:
            providing_args = [obj, "user", "context"]

            if prefix == "pre" and action == "create":
                providing_args += ["validated_data"]

            setattr(
                module,
                f"{prefix}_{action}_{obj}",
                Signal(providing_args=providing_args),
            )

# TODO: remove in the next major release since those are events are deprecated...
# ... in favor of "post_" events
created_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_work_item = Signal(providing_args=["work_item", "user", "context"])
skipped_work_item = Signal(providing_args=["work_item", "user", "context"])
suspended_work_item = Signal(providing_args=["work_item", "user", "context"])
resumed_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_case = Signal(providing_args=["case", "user", "context"])
created_case = Signal(providing_args=["case", "user", "context"])
suspended_case = Signal(providing_args=["case", "user", "context"])
resumed_case = Signal(providing_args=["case", "user", "context"])

# ... also in favor of the american notation
canceled_work_item = Signal(providing_args=["work_item", "user", "context"])
cancelled_work_item = Signal(providing_args=["work_item", "user", "context"])
canceled_case = Signal(providing_args=["case", "user", "context"])
cancelled_case = Signal(providing_args=["case", "user", "context"])

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
