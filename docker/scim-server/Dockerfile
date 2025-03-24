# syntax=docker/dockerfile:1.9
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE_TAG=0.16.1-2025-02-14@sha256:8c25ce5b41977cb59b1e5da1363a4320d985a77d6903d2d9b0dfee1afc1fd22c
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-python-520

###############################################
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11

COPY scim-udm-transformer-lib /app/scim-udm-transformer-lib
COPY pyproject.toml README.md /app/
COPY scim-server/pyproject.toml scim-server/uv.lock /app/scim-server/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --project scim-server/ \
    --locked \
    --no-dev \
    --no-install-project && \
  uv export -o ./scim-server/requirements.txt

COPY scim-server/src /app/scim-server/src
RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable --project scim-server/


##########################################################################
FROM build AS test
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache \
  uv sync --project scim-server/ --dev

# Only necessary once we add helm unittests
# COPY --from=alpine/helm:3.17.1@sha256:e8d29e13b8218a8cb7b117a10a5210922474a74467bf70b6f3f1f7d9c1818ab0 /usr/bin/helm /usr/local/bin/helm

##########################################################################
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/scim-server/.venv/bin:$PATH

RUN \
    groupadd -r scim-server -g 1000 && \
    useradd -r -d /app -g scim-server -N scim-server -u 1000

COPY --from=build --chown=app:app /app/scim-server/.venv /app/scim-server/.venv
COPY --from=build --chown=app:app /app/scim-server/requirements.txt /app/scim-server/

USER scim-server
WORKDIR /app/scim-server

CMD ["scim-server"]

RUN \
  .venv/bin/python3.11 -V && \
  .venv/bin/python3.11 -m site && \
  .venv/bin/python3.11 -c 'import univention.scim.server'
