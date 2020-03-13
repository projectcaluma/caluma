from django.dispatch import Signal

created_work_item = Signal(providing_args=["work_item"])
cancelled_work_item = Signal(providing_args=["work_item"])
completed_work_item = Signal(providing_args=["work_item"])
skipped_work_item = Signal(providing_args=["work_item"])
completed_case = Signal(providing_args=["case"])
created_case = Signal(providing_args=["case"])
cancelled_case = Signal(providing_args=["case"])
