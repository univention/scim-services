# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from copy import deepcopy
from pprint import pformat


def cust_pformat(obj) -> str:
    """
    Custom pformat.

    Can handle objects and is formatted with the Icecream package.

    Returns
    -------
    str
    """
    obj_cp = deepcopy(obj)
    dict_obj = None
    if hasattr(obj_cp, "__dict__"):
        dict_obj = vars(obj_cp)
        for key, value in dict_obj.items():
            if hasattr(value, "__dict__"):
                dict_obj[key] = vars(value)
    final_obj = dict_obj or vars(obj_cp) if hasattr(obj_cp, "dict") else obj_cp
    return pformat(final_obj)


def cust_pprint(obj):
    """
    Custom pprint.

    Can handle objects and is formatted with the Icecream package.
    """
    print(cust_pformat(obj))
