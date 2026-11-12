# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import multiprocessing
from typing import Literal

from loguru import logger

from univention.scim.client.main import run as scim_client_run

from . import scim_helper


class BackgroundConsumer:
    """
    Context manager around a process running the application.

    Can be used as a regular or async context manager. On
    __enter__/__aenter__, creates a provisioning subscription ad starts a
    process that runs the main modules run(). __exit__/__aexit__ tears it down
    again.
    """

    def __init__(self) -> None:
        self._proc = None

    def __enter__(self) -> "BackgroundConsumer":
        assert self._proc is None
        scim_helper.create_provisioning_subscription_sync()
        self._start()
        return self

    def __exit__(self, *_) -> Literal[False]:
        self._stop()
        scim_helper.delete_provisioning_subscription_sync()
        return False

    async def __aenter__(self) -> "BackgroundConsumer":
        assert self._proc is None
        await scim_helper.create_provisioning_subscription()
        self._start()
        return self

    async def __aexit__(self, *_) -> Literal[False]:
        self._stop()
        await scim_helper.delete_provisioning_subscription()
        return False

    def _start(self):
        logger.info("Starting background consumer process.")
        self._proc = multiprocessing.Process(target=scim_client_run)
        self._proc.start()

    def _stop(self):
        assert self._proc is not None
        self._proc.terminate()
        logger.info("Background consumer process terminated.", exitcode=self._proc.exitcode)
