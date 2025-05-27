# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


class MappingError(Exception):
    def __init__(self, message: str, element: str, value: str) -> None:
        super().__init__(message)

        self.element = element
        self.value = value
