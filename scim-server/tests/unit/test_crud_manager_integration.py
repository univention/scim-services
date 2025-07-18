# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


import pytest
from scim2_models import Group, Name, User
from univention.admin.rest.client import UDM

from tests.conftest import CreateGroupFactory, CreateUserFactory
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.crud_manager import CrudManager
from univention.scim.server.domain.repo.udm.crud_udm import CrudUdm
from univention.scim.server.domain.rules.action import Action
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl
from univention.scim.transformation import ScimToUdmMapper, UdmToScimMapper


def create_crud_manager(
    resource_type: str,
    resource_class: type[User | Group],
    udm_client: UDM,
    scim2udm_mapper: ScimToUdmMapper,
    udm2scim_mapper: UdmToScimMapper,
) -> CrudManager:
    repository = CrudUdm(
        resource_type=resource_type,
        scim2udm_mapper=scim2udm_mapper,
        udm2scim_mapper=udm2scim_mapper,
        resource_class=resource_class,
        udm_client=udm_client,
        base_url="http://testserver/scim/v2",
    )

    return CrudManager(repository, resource_type)


@pytest.mark.asyncio
async def test_user_service(
    create_random_user: CreateUserFactory, udm_client: UDM, mappers: tuple[ScimToUdmMapper, UdmToScimMapper]
) -> None:
    print("\n=== Testing User Service ===")

    scim2udm_mapper, udm2scim_mapper = mappers
    user_crud_manager = create_crud_manager(
        "User", User, udm_client, scim2udm_mapper=scim2udm_mapper, udm2scim_mapper=udm2scim_mapper
    )
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
    retrieved_user = udm2scim_mapper.map_user(udm_obj, base_url="http://testserver/scim/v2")
    print(f"Retrieved user: {retrieved_user.display_name}")

    assert retrieved_user.__dict__ == created_user.__dict__


@pytest.mark.asyncio
async def test_group_service(
    create_random_group: CreateGroupFactory, udm_client: UDM, mappers: tuple[ScimToUdmMapper, UdmToScimMapper]
) -> None:
    print("\n=== Testing Group Service ===")

    scim2udm_mapper, udm2scim_mapper = mappers
    group_crud_manager = create_crud_manager(
        "Group", Group, udm_client, scim2udm_mapper=scim2udm_mapper, udm2scim_mapper=udm2scim_mapper
    )
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
    retrieved_group = udm2scim_mapper.map_group(udm_object, base_url="http://testserver/scim/v2")
    print(f"Retrieved group: {retrieved_group.display_name}")

    assert retrieved_group.__dict__ == created_group.__dict__


@pytest.mark.asyncio
async def test_rule_application() -> None:
    print("\n=== Testing Rule Application ===")

    user = User(user_name="john.smith", name=Name(given_name="John", family_name="Smith"))
    print(f"Original user: {user.display_name=}")

    rule_evaluator = RuleEvaluator[User]()
    rule_evaluator.add_rule(UserDisplayNameRule())

    updated_user = await rule_evaluator.evaluate(user, Action.Update)
    print(f"After rules: {updated_user.display_name=}")
    assert updated_user.display_name == "John Smith", "Display name rule failed"
