# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import uuid

from faker import Faker
from faker.providers import address, profile
from loguru import logger
from univention.admin.rest.client import UDM

from univention.scim.consumer.helper import cust_pformat


def generate_udm_users(udm_client: UDM, amount: int, maildomain_name: str):
    fake = Faker(["de_DE"])
    fake.add_provider(address)
    fake.add_provider(profile)

    users = []
    for _i in range(0, amount):
        user_name = fake.unique.simple_profile().get("username")
        user_data = {
            "username": user_name,
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "univentionObjectIdentifier": str(uuid.uuid4()),
            "password": "univention",
            "displayName": fake.name(),
            "e-mail": [fake.email()],
            "street": fake.street_address(),
            "postcode": fake.postcode(),
            "city": fake.city(),
            "country": fake.country(),
            "state": fake.state(),
            "phone": [fake.phone_number()],
            "mailPrimaryAddress": f"{user_name}@{maildomain_name}",
            "mailAlternativeAddress": [f"{user_name}.3@{maildomain_name}", f"{user_name}.2@{maildomain_name}"],
        }
        user = create_udm_user(udm_client=udm_client, user_data=user_data)
        users.append(user)

    logger.info("Created {} testusers in UDM.", _i + 1)

    return users


def create_udm_group(udm_client, group_data):
    logger.info("Create udm group")
    logger.debug("udm group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    logger.debug("udm group module {}", module)
    obj = module.new()
    logger.debug("udm group obj {}", obj)
    for key, value in group_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def update_udm_group(udm_client, group_data):
    logger.info("Update udm group")
    logger.debug("Group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    search = module.search(f"univentionObjectIdentifier={group_data['univentionObjectIdentifier']}")
    result = next(search)
    obj = result.open()

    logger.debug("Found group with uoi: {}", group_data["univentionObjectIdentifier"])
    logger.debug("udm group obj {}", obj)

    for key, value in group_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def delete_udm_group(udm_client, group_data):
    logger.info("Delete udm group")
    logger.debug("Group data:\n{}", cust_pformat(group_data))

    module = udm_client.get("groups/group")
    search = module.search(f"univentionObjectIdentifier={group_data['univentionObjectIdentifier']}")
    result = next(search)
    obj = result.open()

    logger.debug("Found group with uoi: {}", group_data["univentionObjectIdentifier"])

    obj.delete()

    return obj


def create_udm_user(udm_client, user_data):
    logger.info("Create_udm user")
    logger.debug("udm user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    obj = module.new()
    for key, value in user_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def update_udm_user(udm_client, user_data: dict, position: str = None):
    logger.info("Update udm user")
    logger.debug("Do update with user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    search = module.search(f"univentionObjectIdentifier={user_data['univentionObjectIdentifier']}")
    result = next(search)
    obj = result.open()

    logger.debug("Found user with uoi in UDM: {}", user_data["univentionObjectIdentifier"])
    logger.debug("Received UDM user date:\n{}", cust_pformat(obj))

    # For move test
    if position:
        obj.position = position

    for key, value in user_data.items():
        obj.properties[key] = value
    obj.save()

    return obj


def delete_udm_user(udm_client, user_data):
    logger.info("Delete udm user")
    logger.debug("udm user data:\n{}", cust_pformat(user_data))

    module = udm_client.get("users/user")
    search = module.search(f"univentionObjectIdentifier={user_data['univentionObjectIdentifier']}")
    result = next(search)
    obj = result.open()

    logger.debug("Found user with uoi: {}", user_data["univentionObjectIdentifier"])

    obj.delete()

    return obj
