# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.4-build.20260108@sha256:aa219aca5425e467afa8cf3a1eabb2023afa50149702da67402bf65f544cd784

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN mkdir -p /opt/univention/scim-dev-server && mkdir -p /var/log

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && pip3 install --no-cache-dir --break-system-packages scim2-server requests

CMD ["nohup", \
     "scim2-server", \
     "--hostname", "0.0.0.0", \
     "--port", "8080"]
