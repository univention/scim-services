# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2025 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.2-build.20250904@sha256:c93283dd2d42fdf2edcbb2e64b0e37ee11248c0cc624eb3924123da2406d5489

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
