# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from univention.scim.server.authn.fast_api_adapter import FastAPIAuthAdapter
from univention.scim.server.config import application_settings
from univention.scim.server.configure_logging import configure_logging
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.middlewares.request_logging import setup_request_logging_middleware
from univention.scim.server.model_service.load_schemas import LoadSchemas
from univention.scim.server.rest.error_handler import generic_exception_handler, scim_exception_handler
from univention.scim.server.rest.groups import router as groups_router
from univention.scim.server.rest.resource_type import router as resources_types_router
from univention.scim.server.rest.schema import router as schema_router
from univention.scim.server.rest.service_provider import router as service_provider_router
from univention.scim.server.rest.users import router as users_router


settings = application_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage lifespan of FastAPI app"""
    # Initialization tasks when the application starts.
    logger.info("Starting SCIM server")

    container = ApplicationContainer()
    container.wire(packages=["univention.scim.server.rest"])

    # Use settings from container to allow overriding values in unit tests
    settings = ApplicationContainer().settings()

    # We don't want network access at initialization time instead it is fetched at runtime
    # when scim server is starting up
    dependencies = (
        [Security(FastAPIAuthAdapter(container.oidc_configuration().get_configuration()))]
        if settings.auth_enabled
        else None
    )
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

    schema_loader: LoadSchemas = container.schema_loader()

    # Load schemas and perform startup tasks
    try:
        await schema_loader.get_user_schema()
        await schema_loader.get_group_schema()
        await schema_loader.get_service_provider_config_schema()
        resource_types = await schema_loader.get_resource_types()
        logger.info(f"Loaded schemas successfully: {[rt.name for rt in resource_types]}")
    except Exception as e:
        logger.error(f"Failed to load schemas: {e}")
        raise
    yield
    # Cleanup tasks when the application is shutting down
    logger.info("Shutting down SCIM server")


# Configure logging
configure_logging(settings.log_level)

# Setup app
app: FastAPI = FastAPI(
    title="Univention SCIM Server",
    description="SCIM 2.0 API implementation for Univention",
    version="0.1.0",
    lifespan=lifespan,
)

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
app.add_exception_handler(Exception, generic_exception_handler)


def run() -> None:
    """Entry point for running the application."""
    uvicorn.run(
        "univention.scim.server.main:app",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    run()
