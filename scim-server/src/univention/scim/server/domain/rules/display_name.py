# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from loguru import logger
from scim2_models import User
from univention.scim.server.domain.rules.rule import Rule


class UserDisplayNameRule(Rule[User]):
    """
    Rule for user display name.

    Ensures that User objects have a display name, generating one from
    given name and family name if necessary.
    """

    def get_name(self) -> str:
        """Get the rule name."""
        return "UserDisplayNameRule"

    async def apply(self, user: User) -> User:
        """
        Apply the display name rule to a user.

        If the user does not have a display name but has given name and/or
        family name, a display name is generated.

        Args:
            user: The user to apply the rule to

        Returns:
            The user with a display name set
        """
        logger.debug(f"Applying {self.get_name()} to user {user.id}")

        # Skip if display name is already set
        if user.display_name:
            return user

        # Skip if no name object
        if not user.name:
            return user

        # Generate display name from given name and family name
        given = user.name.given_name or ""
        family = user.name.family_name or ""

        if given and family:
            user.display_name = f"{given} {family}"
        elif given:
            user.display_name = given
        elif family:
            user.display_name = family

        logger.debug(f"Generated display name for user {user.id}: {user.display_name}")
        return user
