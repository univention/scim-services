# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging
from importlib.metadata import version  # move to top of file

import uvicorn
from fastapi import FastAPI


# from lancelog import setup_logging


app = FastAPI(title="SCIM API", description="A FastAPI-based SCIM API for identity provisioning", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"msg": "Hello World"}


@app.get("/healthcheck", response_model=dict)
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "SCIM API is running"}


def run() -> None:
    setup_logging()
    logging.info("Starting SCIM server ... version=%s", version("scim-server"))
    logging.info("Listening on http://0.0.0.0:7777")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=7777,
            log_config=None,
        )
    except Exception as exc:
        logging.exception("Failed to start server: %s", exc)
    else:
        logging.info("Server shut down cleanly.")


def setup_logging(log_level: str = "INFO") -> None:
    logging.captureWarnings(True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )


if __name__ == "__main__":
    run()
