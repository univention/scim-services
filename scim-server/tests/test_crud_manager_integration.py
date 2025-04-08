# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
import pytest
from scim2_models import Email, Group, Name, User
from univention.scim.server.domain.group_service_impl import GroupServiceImpl
from univention.scim.server.domain.repo.container import RepositoryContainer
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator
from univention.scim.server.domain.user_service_impl import UserServiceImpl


@pytest.mark.asyncio
async def test_user_service() -> None:
    """Test the UserService implementation with CrudManager."""
    print("\n=== Testing User Service ===")

    # Create a CrudManager for User resources
    # Use the repository container instead of the direct method
    user_crud_manager = RepositoryContainer.create_for_udm("User", User)

    # Create the UserService with the CrudManager
    user_service = UserServiceImpl(user_crud_manager)

    # Create a test user
    new_user = User(
        schemas=["urn:ietf:params:scim:schemas:core:2.0:User"],
        user_name="jane.doe",
        name=Name(given_name="Jane", family_name="Doe"),
        emails=[Email(value="jane.doe@example.com", primary=True, type="work")],
        active=True,
    )

    # Create the user
    print("Creating user...")
    created_user = await user_service.create_user(new_user)
    print(f"User created with ID: {created_user.id}")
    print(f"Display name: {created_user.display_name}")  # Should be set by UserDisplayNameRule

    # Retrieve the user
    print("\nRetrieving user...")
    retrieved_user = await user_service.get_user(created_user.id)
    print(f"Retrieved user: {retrieved_user.display_name}")

    # Update the user
    print("\nUpdating user...")
    retrieved_user.nick_name = "JD"
    updated_user = await user_service.update_user(retrieved_user.id, retrieved_user)
    print(f"Updated user nickname: {updated_user.nick_name}")

    # List users
    print("\nListing users...")
    users_response = await user_service.list_users()
    print(f"Total users: {users_response.total_results}")
    print(f"First user: {users_response.resources[0].display_name}")

    # Delete the user
    print("\nDeleting user...")
    delete_result = await user_service.delete_user(created_user.id)
    print(f"User deleted: {delete_result}")


@pytest.mark.asyncio
async def test_group_service(user_id: str = "test") -> None:
    """Test the GroupService implementation with CrudManager."""
    print("\n=== Testing Group Service ===")

    # Create a CrudManager for Group resources
    # Use the repository container instead of the direct method
    group_crud_manager = RepositoryContainer.create_for_udm("Group", Group)

    # Create the GroupService with the CrudManager
    group_service = GroupServiceImpl(group_crud_manager)

    # Create a test group
    new_group = Group(
        schemas=["urn:ietf:params:scim:schemas:core:2.0:Group"],
        display_name="Engineering Team",
    )

    # Create the group
    print("Creating group...")
    created_group = await group_service.create_group(new_group)
    print(f"Group created with ID: {created_group.id}")

    # Retrieve the group
    print("\nRetrieving group...")
    retrieved_group = await group_service.get_group(created_group.id)
    print(f"Retrieved group: {retrieved_group.display_name}")

    # Update the group
    print("\nUpdating group...")
    retrieved_group.display_name = "Engineering Department"
    updated_group = await group_service.update_group(retrieved_group.id, retrieved_group)
    print(f"Updated group name: {updated_group.display_name}")

    # List groups
    print("\nListing groups...")
    groups_response = await group_service.list_groups()
    print(f"Total groups: {groups_response.total_results}")
    print(f"First group: {groups_response.resources[0].display_name}")

    # Delete the group
    print("\nDeleting group...")
    delete_result = await group_service.delete_group(created_group.id)
    print(f"Group deleted: {delete_result}")


@pytest.mark.asyncio
async def test_rule_application() -> None:
    """Test the application of rules to User resources."""
    print("\n=== Testing Rule Application ===")

    # Create a user without a display name
    user = User(user_name="john.smith", name=Name(given_name="John", family_name="Smith"))
    print(f"Original user: {user.display_name=}")

    # Create rule evaluator with display name rule
    rule_evaluator = RuleEvaluator[User]()
    rule_evaluator.add_rule(UserDisplayNameRule())

    # Apply rules
    updated_user = await rule_evaluator.evaluate(user)
    print(f"After rules: {updated_user.display_name=}")
    assert updated_user.display_name == "John Smith", "Display name rule failed"
