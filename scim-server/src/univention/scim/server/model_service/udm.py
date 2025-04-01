# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from loguru import logger


class UdmClient:
    """
    Client for interacting with the UDM REST API.

    Provides methods for retrieving and manipulating UDM objects.
    """

    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """
        Initialize the UDM client.

        Args:
            base_url: Base URL of the UDM REST API
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url or "http://localhost:8090/univention/udm"
        self.username = username
        self.password = password

    async def get_object(self, module: str, object_id: str) -> dict:
        """
        Get a UDM object by ID.

        Args:
            module: UDM module name (e.g., 'users/user')
            object_id: Object ID

        Returns:
            The UDM object as a dictionary

        Raises:
            ValueError: If the object does not exist
        """
        logger.debug(f"Getting UDM object: {module}/{object_id}")

        # TODO: Implement actual UDM REST API call
        # For now, just return a dummy object
        return {
            "dn": f"uid={object_id},cn=users,dc=example,dc=com",
            "props": {
                "username": f"user{object_id}",
                "firstname": "Test",
                "lastname": "User",
            },
        }

    async def list_objects(self, module: str, filter_str: str = None, position: str = None) -> list[dict]:
        """
        List UDM objects.

        Args:
            module: UDM module name (e.g., 'users/user')
            filter_str: LDAP filter string
            position: LDAP position to search from

        Returns:
            List of UDM objects as dictionaries
        """
        logger.debug(f"Listing UDM objects: {module}, filter: {filter_str}")

        # TODO: Implement actual UDM REST API call
        # For now, just return an empty list
        return []

    async def create_object(self, module: str, properties: dict, position: str = None) -> dict:
        """
        Create a UDM object.

        Args:
            module: UDM module name (e.g., 'users/user')
            properties: Object properties
            position: LDAP position for the new object

        Returns:
            The created UDM object as a dictionary
        """
        logger.debug(f"Creating UDM object: {module}")

        # TODO: Implement actual UDM REST API call
        # For now, just return the input properties with a dummy DN
        return {"dn": "uid=new,cn=users,dc=example,dc=com", "props": properties}

    async def modify_object(self, module: str, object_id: str, properties: dict) -> dict:
        """
        Modify a UDM object.

        Args:
            module: UDM module name (e.g., 'users/user')
            object_id: Object ID
            properties: Object properties to update

        Returns:
            The modified UDM object as a dictionary
        """
        logger.debug(f"Modifying UDM object: {module}/{object_id}")

        # TODO: Implement actual UDM REST API call
        # For now, just return the input properties with a dummy DN
        return {"dn": f"uid={object_id},cn=users,dc=example,dc=com", "props": properties}

    async def delete_object(self, module: str, object_id: str) -> bool:
        """
        Delete a UDM object.

        Args:
            module: UDM module name (e.g., 'users/user')
            object_id: Object ID

        Returns:
            True if the object was deleted
        """
        logger.debug(f"Deleting UDM object: {module}/{object_id}")

        # TODO: Implement actual UDM REST API call
        # For now, just return True to indicate success
        return True
