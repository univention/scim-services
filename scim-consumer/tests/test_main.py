# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import time

from loguru import logger

from univention.scim.consumer.helper import cust_pformat
from univention.scim.consumer.scim_client import ScimClientNoDataFoundException, ScimClientWrapper


def create_udm_user(udm_client, udm_user):
    logger.info("Create_udm user")
    logger.debug("udm user data:\n{}", cust_pformat(udm_user))

    module = udm_client.get("users/user")
    obj = module.new()
    for key, value in udm_user.items():
        obj.properties[key] = value
    obj.save()

    return True


def update_udm_user(udm_client, udm_user):
    logger.info("Update udm user")
    logger.debug("udm user data:\n{}", cust_pformat(udm_user))

    module = udm_client.get("users/user")
    for result in module.search(f"univentionObjectIdentifier={udm_user['univentionObjectIdentifier']}"):
        logger.debug("Found user with uoi: {}", udm_user["univentionObjectIdentifier"])
        obj = result.open()
        for key, value in udm_user.items():
            obj.properties[key] = value

        obj.save()
        break

    return True


def delete_udm_user(udm_client, udm_user):
    logger.info("Delete udm user")
    logger.debug("udm user data:\n{}", cust_pformat(udm_user))

    module = udm_client.get("users/user")
    for result in module.search(f"univentionObjectIdentifier={udm_user['univentionObjectIdentifier']}"):
        logger.debug("Found user with uoi: {}", udm_user["univentionObjectIdentifier"])
        obj = result.open()
        obj.delete()
        break

    return True


def test_scim_crud(udm_client_fixture, scim_consumer, udm_user, udm_user_updated):
    scim_client = ScimClientWrapper()

    # Test create
    create_udm_user(udm_client=udm_client_fixture, udm_user=udm_user)
    for i in range(1, 100):
        try:
            logger.info("Try to get user with uoi: {}. Attemp {}", udm_user.get("univentionObjectIdentifier"), i)
            user = scim_client.get_resource_by_external_id(udm_user.get("univentionObjectIdentifier"))
        except Exception:
            time.sleep(5)
            continue
        else:
            logger.debug("fetched scim user data:\n{}", cust_pformat(user))
            break

    assert user.user_name == udm_user.get("username")

    # Test update
    update_udm_user(udm_client=udm_client_fixture, udm_user=udm_user_updated)
    for i in range(1, 100):
        logger.info("Try to get user with uoi: {}. Attemp {}", udm_user.get("univentionObjectIdentifier"), i)
        user = scim_client.get_resource_by_external_id(udm_user.get("univentionObjectIdentifier"))
        if user.display_name == udm_user_updated.get("displayName"):
            break
        else:
            time.sleep(5)

    assert user.display_name == udm_user_updated.get("displayName")

    # Test delete
    delete_udm_user(udm_client=udm_client_fixture, udm_user=udm_user)
    throws_exception = False
    try:
        for i in range(1, 100):
            logger.info("Try to get user with uoi: {}. Attemp {}", udm_user.get("univentionObjectIdentifier"), i)
            user = scim_client.get_resource_by_external_id(udm_user.get("univentionObjectIdentifier"))
            time.sleep(5)

    except ScimClientNoDataFoundException:
        throws_exception = True
    assert throws_exception
