# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from fastapi import FastAPI


app = FastAPI(title="SCIM API", description="A FastAPI-based SCIM API for identity provisioning", version="1.0.0")


@app.get("/")
async def root() -> dict[str, str]:
    return {"msg": "Hello World"}


@app.get("/healthcheck", response_model=dict)
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "SCIM API is running"}
