# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import uvicorn
from fastapi import FastAPI


app = FastAPI(title="SCIM API", description="A FastAPI-based SCIM API for identity provisioning", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"msg": "Hello World"}


@app.get("/healthcheck", response_model=dict)
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "SCIM API is running"}


def run() -> None:
    # settings = app_settings()
    # assert settings
    # setup_logging(settings.log_level)
    print("Ready to receive requests")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        log_config=None,
    )


if __name__ == "__main__":
    run()
