# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_save_option 1"] = {
    "saveOption": {"option": {"label": "Jordan Mccarthy", "slug": "mrs-shake-recent"}}
}
