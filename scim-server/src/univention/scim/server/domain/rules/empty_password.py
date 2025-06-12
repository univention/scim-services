# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import secrets
import string
from random import shuffle

from loguru import logger
from scim2_models import User

from univention.scim.server.domain.rules.action import Action
from univention.scim.server.domain.rules.rule import Rule


class UserEmptyPasswordRule(Rule[User]):
    """
    Rule for user empty password.

    * For POST requests with a password: the password is assigned to the user.
    * For POST requests with an empty password: an error is returned.
    * For POST requests without a password (key): a random password is assigned to the user.
    * For PUT requests with a password: the password is assigned to the user.
    * For PUT requests with an empty password: an error is returned.
    * For PUT requests without a password: the current password is kept. (current state)
    * For PATCH requests with the password set: the password is assigned to the user.
    """

    def _get_random_password(self) -> str:
        chars = [
            *[secrets.choice(string.ascii_lowercase) for i in range(10)],
            *[secrets.choice(string.ascii_uppercase) for i in range(10)],
            *[secrets.choice(string.digits) for i in range(8)],
            *[secrets.choice(string.punctuation) for i in range(4)],
        ]
        shuffle(chars)

        return "".join(chars)

    def get_name(self) -> str:
        """Get the rule name."""
        return "UserEmptyPasswordRule"

    async def apply(self, user: User, action: Action) -> User:
        """
        Apply the password rule to a user.

        Args:
            user: The user to apply the rule to
            action: The action which triggered the rule

        Returns:
            The user with a generated password
        """

        logger.debug(f"Applying {self.get_name()} to user {user.id}")

        if user.password:
            return user

        if user.password is None:
            if action == Action.Create:
                logger.debug(f"Generated random password for user {user.id}")
                user.password = self._get_random_password()
                user.ignore_password_policy = True
        elif len(user.password) == 0:
            logger.error("Empty password is not allowed")
            raise ValueError("Empty password is not allowed")

        return user
