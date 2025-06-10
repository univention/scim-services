# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


from collections.abc import Callable
from typing import Any

from asgi_correlation_id import correlation_id
from lancelog import setup_logging
from loguru import logger


def configure_logging(log_level: str) -> None:
    """
    Configure logging for the application using lancelog and loguru with correlation ID support.
    """
    # First, set up lancelog with the basic configuration
    setup_logging(
        level=log_level,
    )

    # Store the original patcher function
    original_patcher: Callable[[dict[str, Any]], dict[str, Any]] | None = logger._core.patcher

    # Create a new patcher that combines the original with our correlation ID addition
    def combined_patcher(record: dict[str, Any]) -> dict[str, Any]:
        # First apply the original patcher
        if original_patcher:
            original_patcher(record)

        # Ensure the extra dict exists
        if "extra" not in record or record["extra"] is None:
            record["extra"] = {}

        # Then add correlation ID
        record["extra"]["correlation_id"] = correlation_id.get() or "-"
        return record

    # Apply the combined patcher
    logger.configure(patcher=combined_patcher)
