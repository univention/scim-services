# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os
from collections.abc import Callable

import pytest
from scim2_models import Group, Name, User
from univention.admin.rest.client import UDM

from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper

from .conftest import create_crud_manager, skip_if_no_udm


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("maildomain")
async def test_user_service(create_random_user: Callable[[], User]) -> None:
    print("\n=== Testing User Service ===")

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    ScimToUdmMapper()
    udm2scim_mapper = UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    user_crud_manager = create_crud_manager("User", User, udm_url, udm_username, udm_password)
    UserServiceImpl(user_crud_manager)

    created_user = await create_random_user()
    print(f"Using user with ID: {created_user.id}")
    print(f"Display name: {created_user.display_name}")

    print("\nRetrieving user with UDM client...")
    module = udm_client.get("users/user")
    filter_str = f"univentionObjectIdentifier={created_user.id}"
    results = list(module.search(filter_str))

    assert results, f"User with ID {created_user.id} not found"
    udm_obj = results[0].open()
    retrieved_user = udm2scim_mapper.map_user(udm_obj, base_url=udm_url)
    print(f"Retrieved user: {retrieved_user.display_name}")

    assert retrieved_user.__dict__ == created_user.__dict__


@pytest.mark.asyncio
@pytest.mark.skipif(skip_if_no_udm(), reason="UDM server not reachable or in unit tests only mode")
@pytest.mark.usefixtures("maildomain")
async def test_group_service(create_random_group: Callable[[], Group]) -> None:
    print("\n=== Testing Group Service ===")

    udm_url = os.environ.get("UDM_URL", "http://localhost:9979/univention/udm")
    udm_username = os.environ.get("UDM_USERNAME", "admin")
    udm_password = os.environ.get("UDM_PASSWORD", "univention")

    ScimToUdmMapper()
    UdmToScimMapper()

    udm_client = UDM.http(udm_url, udm_username, udm_password)

    group_crud_manager = create_crud_manager("Group", Group, udm_url, udm_username, udm_password)
    GroupServiceImpl(group_crud_manager)

    created_group = await create_random_group()
    print(f"Using group with ID: {created_group.id}")

    print("\nRetrieving group with UDM client...")
    module = udm_client.get("groups/group")
    filter_str = f"univentionObjectIdentifier={created_group.id}"
    results = list(module.search(filter_str))

    assert results, f"Group with ID {created_group.id} not found"
    results[0].open()
    udm_object = results[0].open()
    retrieved_group = UdmToScimMapper().map_group(udm_object, base_url=udm_url)
    print(f"Retrieved group: {retrieved_group.display_name}")

    assert retrieved_group.__dict__ == created_group.__dict__


@pytest.mark.asyncio
async def test_rule_application() -> None:
    print("\n=== Testing Rule Application ===")

    user = User(user_name="john.smith", name=Name(given_name="John", family_name="Smith"))
    print(f"Original user: {user.display_name=}")

    rule_evaluator = RuleEvaluator[User]()
    rule_evaluator.add_rule(UserDisplayNameRule())

    updated_user = await rule_evaluator.evaluate(user)
    print(f"After rules: {updated_user.display_name=}")
    assert updated_user.display_name == "John Smith", "Display name rule failed"
