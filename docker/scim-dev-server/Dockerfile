# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN mkdir -p /opt/univention/scim-dev-server && mkdir -p /var/log

COPY docker/scim-dev-server/requirements.txt /opt/univention/scim-dev-server

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && pip3 install --no-cache-dir --break-system-packages -r /opt/univention/scim-dev-server/requirements.txt

CMD nohup scim2-server --hostname ${SCIM_SERVER_HOSTNAME} \
                       --port 8080 \
                       --resource-type /opt/univention/scim-dev-server/resource-types.json \
                       --schema /opt/univention/scim-dev-server/schemas.json \
      > /var/log/scim-dev-server.log 2>&1
