# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from loguru import logger


def add_timing_middleware(
    app: FastAPI,
    prefix: str = "",
) -> None:
    """
    Add timing middleware to the FastAPI application.

    This middleware logs the processing time for each request in milliseconds.

    Args:
        app: The FastAPI application to add the middleware to.
        prefix: A prefix to add to log messages (optional).
    """

    @app.middleware("http")
    async def timing_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Get the route path for the request
        route_path = request.url.path

        # Record start time
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate processing time in milliseconds
        process_time = (time.time() - start_time) * 1000

        # Log the timing information with structured logging
        logger.info(
            f"{prefix}Request timing",
            request_path=route_path,
            request_method=request.method,
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
        )

        return response


def record_timing(request: Request, name: str) -> None:
    """
    Record an intermediate timing for a request.

    This can be used to measure specific parts of request processing.

    Args:
        request: The request to record timing for.
        name: The name of the timing point.
    """
    if not hasattr(request.state, "start_time"):
        logger.warning("Timing middleware not installed or not properly initialized")
        return

    process_time = (time.time() - request.state.start_time) * 1000
    route_path = request.url.path

    logger.info(
        f"Intermediate timing: {name}",
        request_path=route_path,
        request_method=request.method,
        timing_point=name,
        elapsed_ms=round(process_time, 2),
    )
