# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from scim2_models import Resource

from univention.scim.server.domain.rules.action import Action


T = TypeVar("T", bound=Resource)


class Rule(Generic[T], ABC):
    """
    Interface for business rules.

    Rules encapsulate business logic for validating and transforming resources.
    """

    @abstractmethod
    async def apply(self, resource: T, action: Action) -> T:
        """
        Apply the rule to a resource.

        Args:
            resource: The resource to apply the rule to
            action: The action which triggered the rule

        Returns:
            The transformed resource

        Raises:
            ValueError: If the resource does not satisfy the rule
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the rule.

        Returns:
            The rule name
        """
        pass
