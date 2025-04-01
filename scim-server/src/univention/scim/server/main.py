# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from scim2_models import Error

# Internal imports
from univention.scim.server.configure_logging import configure_logging
from univention.scim.server.container import ApplicationContainer
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_scim_impl import CrudScimImpl
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.model_service.load_schemas_impl import LoadSchemasImpl
from univention.scim.server.rest.api import get_api_router
from univention.scim.server.rest.groups import set_group_service
from univention.scim.server.rest.users import set_user_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage lifespan of FastAPI app"""
    # Initialization tasks when the application starts.
    logger.info("Starting SCIM server")

    # TODO: move to di
    # Initialize dependencies
    schema_loader = LoadSchemasImpl()

    # Create repositories
    user_repository = CrudScimImpl()
    group_repository = CrudScimImpl()

    # Create services
    user_service = UserServiceImpl(user_repository)
    group_service = GroupServiceImpl(group_repository)

    # Inject services into routers
    set_user_service(user_service)
    set_group_service(group_service)

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


# Setup app
# Don't use global variables it easily interferes with testing because
# objects are only created once and keep there state between several tests
def create_app() -> FastAPI:
    # Container for dependency injection
    container = ApplicationContainer()

    # Configure logging
    configure_logging(container.settings().log_level)

    app = FastAPI(
        title="Univention SCIM Server",
        description="SCIM 2.0 API implementation for Univention",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=container.settings().cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup error handling
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception: {exc}")
        error = Error(status="500", detail=str(exc), schemas=["urn:ietf:params:scim:api:messages:2.0:Error"])
        return JSONResponse(status_code=500, content=error.model_dump(scim_ctx=None))

    @app.get("/")
    async def root() -> dict[str, str]:
        """Welcome endpoint with link to documentation."""
        return {"msg": "Hello World"}

    # Include API router
    app.include_router(get_api_router(), prefix=container.settings().api_prefix)

    return app


def run() -> None:
    create_app()
    """Entry point for running the application."""
    uvicorn.run(
        "univention.scim.server.main:app",
        host=ApplicationContainer.settings().host,
        port=ApplicationContainer.settings().port,
    )


if __name__ == "__main__":
    run()
