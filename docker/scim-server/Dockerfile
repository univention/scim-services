# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.2-build.20250714

###############################################
# Stage 0: get build tools
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS tools
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

# A glibc-based uv binary is currently necessary for dns resolution of private pypi repos: https://github.com/astral-sh/uv/issues/8450
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      wget \
      ca-certificates \
    && wget -qO- https://github.com/astral-sh/uv/releases/download/0.7.11/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xz --strip-components=1 -C /usr/local/bin/

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=tools /usr/local/bin/uv /usr/local/bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11

COPY ./pyproject.toml ./uv.lock /app/
COPY ./scim-udm-transformer-lib/pyproject.toml /app/scim-udm-transformer-lib/
COPY ./scim-server/pyproject.toml /app/scim-server/

WORKDIR /app

# copy source code
COPY ./scim-server/src /app/scim-server/src
COPY ./scim-udm-transformer-lib/src /app/scim-udm-transformer-lib/src

RUN uv sync \
        --package=scim-server \
        --no-dev \
        --no-editable \
        --frozen

###############################################
# Stage 2: test
FROM build AS test
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin:$PATH

COPY ./scim-server/tests /app/scim-server/tests

ARG USER=scim-server
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
    rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    groupadd -r ${USER} -g 1000 && \
    useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/.venv /app/.venv

RUN uv sync \
        --package=scim-server \
        --dev \
        --frozen

USER ${USER}

ENTRYPOINT [ \
    "pytest", \
    "--config-file=/app/scim-server/pyproject.toml", \
    "--cov-config=/app/scim-server/pyproject.toml", \
    "--cov-report=xml:/tmp/scim-coverage.xml", \
    "-p", "no:cacheprovider", \
    "scim-server/tests" \
]

###############################################
# Stage 3: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin:$PATH

ARG USER=scim-server
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
    rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    groupadd -r ${USER} -g 1000 && \
    useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/.venv /app/.venv

USER ${USER}

COPY docker/scim-server/scim-server-entrypoint.sh /entrypoint.sh
COPY docker/scim-server/create_ldap_attributes.py /create_ldap_attributes.py
ENTRYPOINT ["/entrypoint.sh"]
