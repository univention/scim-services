# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scim2_models import Resource


T = TypeVar("T", bound=Resource)


class CrudScim(Generic[T], ABC):
    """
    Interface for CRUD operations on SCIM resources.
    This is the domain port to be implemented by infrastructure adapters.
    """

    @abstractmethod
    async def get(self, resource_id: str) -> T:
        """
        Retrieve a resource by ID.
        Args:
            resource_id: The resource's unique identifier
        Returns:
            The resource if found, None otherwise
        """
        pass

    @abstractmethod
    async def list(self, filter_str: str | None = None, start_index: int = 1, count: int | None = None) -> list[T]:
        """
        List resources with optional filtering and pagination.
        Args:
            filter_str: SCIM filter expression
            start_index: 1-based index for the first result
            count: Maximum number of results to return
        Returns:
            List of resources matching the criteria
        """
        pass

    @abstractmethod
    async def count(self, filter_str: str | None = None) -> int:
        """
        Count resources matching a filter.
        Args:
            filter_str: SCIM filter expression
        Returns:
            Number of matching resources
        """
        pass

    @abstractmethod
    async def create(self, resource: T) -> T:
        """
        Create a new resource.
        Args:
            resource: The resource to create
        Returns:
            The created resource with ID assigned
        Raises:
            ValueError: If the resource cannot be created
        """
        pass

    @abstractmethod
    async def update(self, resource_id: str, resource: T) -> T:
        """
        Update an existing resource.
        Args:
            resource_id: The resource's unique identifier
            resource: The updated resource data
        Returns:
            The updated resource
        Raises:
            ValueError: If the resource cannot be updated
        """
        pass

    @abstractmethod
    async def delete(self, resource_id: str) -> bool:
        """
        Delete a resource.
        Args:
            resource_id: The resource's unique identifier
        Returns:
            True if the resource was deleted, False otherwise
        """
        pass
