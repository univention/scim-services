# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from loguru import logger
from scim2_models import Group

from univention.scim.server.model_service.udm import UdmClient


class GroupModel:
    """
    Model service for Group resources.

    Provides methods for mapping between SCIM Group and UDM group objects.
    """

    def __init__(self, udm_client: UdmClient = None):
        """
        Initialize the group model service.

        Args:
            udm_client: UDM client for UDM operations
        """
        self.udm_client = udm_client or UdmClient()

    async def get_group_by_id(self, group_id: str) -> Group:
        """
        Get a SCIM Group by ID.

        Args:
            group_id: Group ID

        Returns:
            SCIM Group object

        Raises:
            ValueError: If the group does not exist
        """
        logger.debug(f"Getting group by ID: {group_id}")

        # Get UDM group
        udm_group = await self.udm_client.get_object("groups/group", group_id)

        # Map UDM group to SCIM Group
        # TODO: Implement proper mapping
        group = Group(
            id=group_id,
            display_name=udm_group["props"].get("name", ""),
        )

        return group

    async def create_group(self, group: Group) -> Group:
        """
        Create a group in UDM from a SCIM Group.

        Args:
            group: SCIM Group object

        Returns:
            Created SCIM Group with UDM ID
        """
        logger.debug("Creating group in UDM")

        # Map SCIM Group to UDM properties
        # TODO: Implement proper mapping
        properties = {
            "name": group.display_name,
        }

        # Create UDM group
        await self.udm_client.create_object("groups/group", properties)

        # Extract group ID from DN
        # TODO: Implement proper ID extraction
        group_id = "new"

        # Update SCIM Group with UDM ID
        group.id = group_id

        return group
