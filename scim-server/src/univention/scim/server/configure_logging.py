# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import os

from lancelog import setup_logging
from univention.scim.server.config import settings


def configure_logging():
    """
    Configure logging for the application using lancelog and loguru.
    """
    # Get log level from settings or environment
    log_level = os.environ.get("LOG_LEVEL", settings.log_level)

    # Use lancelog for structured logging setup
    setup_logging(
        level=log_level,
    )
