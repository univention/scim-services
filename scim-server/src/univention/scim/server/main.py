# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging

import uvicorn
from fastapi import FastAPI


app = FastAPI(title="SCIM API", description="A FastAPI-based SCIM API for identity provisioning", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"msg": "Hello World"}


@app.get("/healthcheck", response_model=dict)
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "SCIM API is running"}


logger = logging.getLogger("scim-server")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


def run() -> None:
    logger.info("Starting SCIM server...")
    logger.info("Listening on http://0.0.0.0:7777")
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=7777,
            log_config=None,
        )
    except Exception as e:
        logger.exception("Failed to start server: %s", e)
    else:
        logger.info("Server shut down cleanly.")


if __name__ == "__main__":
    run()
