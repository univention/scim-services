# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from copy import deepcopy


def vars_recursive(obj):
    # WTF!!?? Python sucks!!!
    obj_cp = deepcopy(obj)
    dict_obj = None
    if hasattr(obj_cp, "__dict__"):
        dict_obj = vars(obj_cp)
        for key, value in dict_obj.items():
            if hasattr(value, "__dict__"):
                dict_obj[key] = vars(value)
    return dict_obj or vars(obj_cp) if hasattr(obj_cp, "dict") else obj_cp
