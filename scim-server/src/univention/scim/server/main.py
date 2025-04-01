# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from scim2_models import Error

# Internal imports
from univention.scim.server.config import settings
from univention.scim.server.configure_logging import configure_logging
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_scim_impl import CrudScimImpl
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.server.model_service.load_schemas_impl import LoadSchemasImpl
from univention.scim.server.rest.api import router as api_router
from univention.scim.server.rest.groups import set_group_service
from univention.scim.server.rest.users import set_user_service


# Configure logging
configure_logging()

# Create FastAPI app
app = FastAPI(
    title="Univention SCIM Server",
    description="SCIM 2.0 API implementation for Univention",
    version="0.1.0",
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
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    error = Error(status="500", detail=str(exc), schemas=["urn:ietf:params:scim:api:messages:2.0:Error"])
    return JSONResponse(status_code=500, content=error.model_dump(scim_ctx=None))


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

# Include API router
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Welcome endpoint with link to documentation."""
    return {"msg": "Hello World"}


@app.on_event("startup")
async def startup_event():
    """Initialization tasks when the application starts."""
    logger.info("Starting SCIM server")
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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks when the application is shutting down."""
    logger.info("Shutting down SCIM server")


def run():
    """Entry point for running the application."""
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run("univention.scim.server.main:app", host=settings.host, port=port)


if __name__ == "__main__":
    run()
