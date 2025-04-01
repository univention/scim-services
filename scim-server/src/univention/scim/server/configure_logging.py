# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from lancelog import setup_logging


def configure_logging(log_level: str) -> None:
    """
    Configure logging for the application using lancelog and loguru.
    """

    # Use lancelog for structured logging setup
    setup_logging(
        level=log_level,
    )
