# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import Counter


def list_duplicates(iterable):
    """Return a set of duplicates in given iterator."""
    return {key for key, count in Counter(iterable).items() if count > 1}
