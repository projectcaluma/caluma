from django.dispatch import Signal

created_work_item = Signal(providing_args=["work_item", "user", "context"])
canceled_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_work_item = Signal(providing_args=["work_item", "user", "context"])
skipped_work_item = Signal(providing_args=["work_item", "user", "context"])
suspended_work_item = Signal(providing_args=["work_item", "user", "context"])
resumed_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_case = Signal(providing_args=["case", "user", "context"])
created_case = Signal(providing_args=["case", "user", "context"])
canceled_case = Signal(providing_args=["case", "user", "context"])
suspended_case = Signal(providing_args=["case", "user", "context"])
resumed_case = Signal(providing_args=["case", "user", "context"])

# TODO: remove in the next major release since those are events are deprecated
# in favor of the american notation
cancelled_work_item = Signal(providing_args=["work_item", "user", "context"])
cancelled_case = Signal(providing_args=["case", "user", "context"])

for (event, old, new) in [
    (cancelled_case, "cancelled_case", "canceled_case"),
    (cancelled_work_item, "cancelled_work_item", "canceled_work_item"),
]:
    event._deprecation_reason = f"`caluma_workflow.events.{old}` is deprecated in favor of `caluma_workflow.events.{new}` and will be removed in the next major version."
