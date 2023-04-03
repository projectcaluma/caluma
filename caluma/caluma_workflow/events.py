import sys

from django.dispatch import Signal

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
