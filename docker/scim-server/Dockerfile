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
COPY scim-server /app/scim-server
COPY udm-to-scim-sync /app/udm-to-scim-sync
COPY pyproject.toml README.md /app/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache uv build scim-udm-transformer-lib
RUN --mount=type=cache,target=/root/.cache uv build udm-to-scim-sync
RUN --mount=type=cache,target=/root/.cache uv build scim-server

##########################################################################
# Test stage: Contains all tools to run unit tests
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS test
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]
WORKDIR /app

# unbuffered output
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

# Only necessary once we add helm unittests
# COPY --from=alpine/helm:3.17.1@sha256:e8d29e13b8218a8cb7b117a10a5210922474a74467bf70b6f3f1f7d9c1818ab0 /usr/bin/helm /usr/local/bin/helm

CMD ["sh", "-c", "uv sync && uv run pytest"]

##########################################################################
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1

RUN \
    groupadd -r scim-server -g 1000 && \
    useradd -r -d /app -g scim-server -N scim-server -u 1000

COPY --from=build --chown=scim-server:scim-server /app/dist/ /app/

RUN apt install -y python3-pip
RUN pip3 install --break-system-packages --no-cache-dir --extra-index-url https://git.knut.univention.de/api/v4/projects/1449/packages/pypi/simple /app/*.whl

WORKDIR /app/
USER scim-server

CMD ["scim-server"]
