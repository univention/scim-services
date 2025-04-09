# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from scim2_models import Error

from univention.scim.server.authn.fast_api_adapter import FastAPIAuthAdapter
from univention.scim.server.config import application_settings
from univention.scim.server.configure_logging import configure_logging
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.model_service.load_schemas import LoadSchemas
from univention.scim.server.rest.groups import router as groups_router
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
app = FastAPI(
    title="Univention SCIM Server",
    description="SCIM 2.0 API implementation for Univention",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup error handling
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    error = Error(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc),
        schemas=["urn:ietf:params:scim:api:messages:2.0:Error"],
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error.model_dump(scim_ctx=None))


def run() -> None:
    """Entry point for running the application."""
    uvicorn.run(
        "univention.scim.server.main:app",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    run()
