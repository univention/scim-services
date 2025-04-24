# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from scim2_models import User

from univention.scim.server.model_service.udm import UdmClient
from univention.scim.transformation import UdmToScimMapper


class UserModel:
    """
    Model service for User resources.

    Provides methods for mapping between SCIM User and UDM user objects.
    """

    def __init__(self, udm_client: UdmClient = None, udm_mapper: UdmToScimMapper = None):
        """
        Initialize the user model service.

        Args:
            udm_client: UDM client for UDM operations
            udm_mapper: Mapper between UDM and SCIM objects
        """
        self.udm_client = udm_client or UdmClient()
        self.udm_mapper = udm_mapper or UdmToScimMapper()

    async def get_user_by_id(self, user_id: str, base_url: str = "") -> User:
        """
        Get a SCIM User by ID.

        Args:
            user_id: User ID
            base_url: Base URL for resource location

        Returns:
            SCIM User object

        Raises:
            ValueError: If the user does not exist
        """
        logger.debug(f"Getting user by ID: {user_id}")

        # Get UDM user
        udm_user = await self.udm_client.get_object("users/user", user_id)

        # Map UDM user to SCIM User using the mapper
        user = self.udm_mapper.map_user(udm_user, base_url)

        return user

    async def create_user(self, user: User) -> User:
        """
        Create a user in UDM from a SCIM User.

        Args:
            user: SCIM User object

        Returns:
            Created SCIM User with UDM ID
        """
        logger.debug("Creating user in UDM")

        # Map SCIM User to UDM properties
        # TODO: Implement proper mapping
        properties = {
            "username": user.user_name,
            "firstname": user.name.given_name if user.name else "",
            "lastname": user.name.family_name if user.name else "",
        }

        # Create UDM user
        await self.udm_client.create_object("users/user", properties)

        # Extract user ID from DN
        # TODO: Implement proper ID extraction
        user_id = "new"

        # Update SCIM User with UDM ID
        user.id = user_id

        return user
