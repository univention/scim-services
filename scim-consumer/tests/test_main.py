# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time

from loguru import logger

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClientWrapper


def test_scim_create_user(create_udm_user, scim_consumer, udm_user):
    logger.info("Test test_scim_create_user started.")
    logger.debug("udm_user:\n{}", cust_pformat(udm_user))

    user = None
    max_loops = 100
    count_loops = 0
    sleep_time = 5

    while True:
        try:
            logger.info("Try to get user with uoi: {}", udm_user.get("univentionObjectIdentifier"))
            user = ScimClientWrapper().get_resource_by_external_id(udm_user.get("univentionObjectIdentifier"))

        except Exception:
            time.sleep(sleep_time)
            count_loops += 1
            if count_loops >= max_loops:
                logger.error("Max loop count reached!")
                break

        else:
            logger.debug("user:\n{}", cust_pformat(user))
            break

    assert user.user_name == udm_user.get("username")
    logger.info("Test test_scim_create_user stopped.")


def test_scim_update_user(update_udm_user, scim_consumer, udm_user_updated):
    logger.info("Test test_scim_update_user started.")
    logger.debug("udm_user_updated:\n{}", cust_pformat(udm_user_updated))

    user = None
    max_loops = 100
    count_loops = 0
    sleep_time = 5

    scim_client = ScimClientWrapper()

    while True:
        try:
            logger.info("Try to get user with uoi: {}", udm_user_updated.get("univentionObjectIdentifier"))
            user = scim_client.get_resource_by_external_id(udm_user_updated.get("univentionObjectIdentifier"))

        except Exception:
            time.sleep(sleep_time)
            count_loops += 1
            if count_loops >= max_loops:
                logger.error("Max loop count reached!")
                break

        else:
            # Maybe not updated until now and old data is still in SCIM ...
            if user.display_name != udm_user_updated.get("displayName"):
                time.sleep(sleep_time)
                count_loops += 1
                if count_loops >= max_loops:
                    logger.error("Max loop count reached!")
                    break
                continue
            else:
                logger.debug("user:\n{}", cust_pformat(user))
                break

    assert user.display_name == udm_user_updated.get("displayName")

    logger.info("Test test_scim_update_user stopped.")


def test_scim_delete_user(delete_udm_user, scim_consumer, udm_user):
    logger.info("Test test_scim_delete_user started.")
    logger.debug("udm_user:\n{}", cust_pformat(udm_user))

    logger.info("Try to get user with uoi: {}", udm_user.get("univentionObjectIdentifier"))

    max_loops = 100
    sleep_time = 5
    count_loops = 0
    throws_exception = False

    scim_client = ScimClientWrapper()
    while True:
        try:
            logger.info("Try to get user with uoi: {}", udm_user.get("univentionObjectIdentifier"))
            scim_client.get_resource_by_external_id(udm_user.get("univentionObjectIdentifier"))

        except Exception:
            throws_exception = True
            break

        else:
            # Maybe not deleted until now ...
            time.sleep(sleep_time)
            count_loops += 1
            if count_loops >= max_loops:
                logger.error("Max loop count reached!")
                break
            continue

    assert throws_exception

    logger.info("Test test_scim_delete_user stopped.")
