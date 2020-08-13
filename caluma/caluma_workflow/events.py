from django.dispatch import Signal

created_work_item = Signal(providing_args=["work_item", "user", "context"])
cancelled_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_work_item = Signal(providing_args=["work_item", "user", "context"])
skipped_work_item = Signal(providing_args=["work_item", "user", "context"])
completed_case = Signal(providing_args=["case", "user", "context"])
created_case = Signal(providing_args=["case", "user", "context"])
cancelled_case = Signal(providing_args=["case", "user", "context"])
