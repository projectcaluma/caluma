# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from graphql_relay import from_global_id


def extract_global_id(id):
    """
    Extract id from global id throwing away type.

    In case it is not a base64 encoded value it will return id as is.
    This way it can be used as input type by simply defining id without its specific type.
    """

    try:
        _, result = from_global_id(id)
    except ValueError:
        result = id

    return result
