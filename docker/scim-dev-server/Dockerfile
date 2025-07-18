# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.2-build.20250714

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN mkdir -p /opt/univention/scim-dev-server && mkdir -p /var/log

COPY docker/scim-dev-server/scim-server-schemas.json /opt/univention/scim-dev-server/schemas.json
COPY docker/scim-dev-server/scim-server-resource-types.json /opt/univention/scim-dev-server/resource-types.json

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && pip3 install --no-cache-dir --break-system-packages scim2-server

CMD ["nohup", \
     "scim2-server", \
     "--hostname", "0.0.0.0", \
     "--port", "8080", \
     "--resource-type", "/opt/univention/scim-dev-server/resource-types.json", \
     "--schema", "/opt/univention/scim-dev-server/schemas.json"]
