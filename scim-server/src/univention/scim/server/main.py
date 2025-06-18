# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, Security
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from univention.scim.server.config import ApplicationSettings, application_settings
from univention.scim.server.configure_logging import configure_logging
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.fast_api_auth_adapter import FastAPIAuthAdapter
from univention.scim.server.middlewares.request_logging import setup_request_logging_middleware
from univention.scim.server.middlewares.timing import add_timing_middleware
from univention.scim.server.rest.error_handler import (
    fastapi_request_exception_handler,
    generic_exception_handler,
    scim_exception_handler,
)
from univention.scim.server.rest.groups import router as groups_router
from univention.scim.server.rest.id import router as id_router
from univention.scim.server.rest.resource_type import router as resources_types_router
from univention.scim.server.rest.schema import router as schema_router
from univention.scim.server.rest.service_provider import router as service_provider_router
from univention.scim.server.rest.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage lifespan of FastAPI app"""
    # Initialization tasks when the application starts.
    logger.info("Starting SCIM server")

    container = ApplicationContainer()
    container.wire(packages=["univention.scim.server.rest"])

    # Use settings from container to allow overriding values in unit tests
    settings = ApplicationContainer().settings()

    dependencies = []
    if settings.auth_enabled:
        # The FastAPI OAuth2AuthorizationCodeBearer requires some information from the IDP
        # which is fetched via network so initialize it here at runtime because
        # we don't want network access at initialization time
        auth = FastAPIAuthAdapter(
            container.oidc_configuration().get_configuration(), container.authenticator(), container.authorization()
        )
        dependencies.append(Security(auth))

    app.include_router(users_router, prefix=f"{settings.api_prefix}/Users", tags=["Users"], dependencies=dependencies)
    app.include_router(
        groups_router, prefix=f"{settings.api_prefix}/Groups", tags=["Groups"], dependencies=dependencies
    )
    app.include_router(
        service_provider_router,
        prefix=f"{settings.api_prefix}/ServiceProviderConfig",
        tags=["ServiceProviderConfig"],
        dependencies=dependencies,
    )
    app.include_router(
        schema_router,
        prefix=f"{settings.api_prefix}/Schemas",
        tags=["Schemas"],
        dependencies=dependencies,
    )
    app.include_router(
        resources_types_router,
        prefix=f"{settings.api_prefix}/ResourceTypes",
        tags=["SCIM"],
        dependencies=dependencies,
    )
    app.include_router(
        id_router,
        prefix=f"{settings.api_prefix}",
        tags=["SCIM"],
        dependencies=dependencies,
    )

    yield
    # Cleanup tasks when the application is shutting down
    logger.info("Shutting down SCIM server")


# Use a function to create the app, this allows the tests to always use a new app object
# reusing the same global app object seems to sporadically break the tests with very wired
# FastAPI errors
def make_app(settings: ApplicationSettings) -> FastAPI:
    # Configure logging
    configure_logging(settings.log_level)

    docs_url = None
    redoc_url = None
    openapi_url = None
    swagger_ui_init_oauth = None

    if settings.docu.enabled:
        logger.info("Enabling docu endpoints")
        docs_url = "/docs"
        redoc_url = "/redoc"
        openapi_url = "/openapi.json"
        swagger_ui_init_oauth = {
            "clientId": settings.docu.client_id,
            "clientSecret": settings.docu.client_secret,
            "appName": "Nubus SCIM-API documentation",
        }

    # Setup app
    app: FastAPI = FastAPI(
        title="Univention SCIM Server",
        description="SCIM 2.0 API implementation for Univention",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        swagger_ui_init_oauth=swagger_ui_init_oauth,
    )

    # Add correlation ID middleware
    app.add_middleware(CorrelationIdMiddleware)

    # Add timing middleware (before request logging middleware)
    add_timing_middleware(app, prefix="SCIM ")

    # Add request logging middleware
    setup_request_logging_middleware(app)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(HTTPException, scim_exception_handler)
    app.add_exception_handler(RequestValidationError, fastapi_request_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    return app


settings = application_settings()
app = make_app(settings)


def run() -> None:
    """Entry point for running the application."""
    uvicorn.run(
        "univention.scim.server.main:app",
        host=settings.listen,
        port=settings.port,
    )


if __name__ == "__main__":
    run()
