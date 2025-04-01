# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH
from loguru import logger
from univention.scim.server.domain.rules.display_name import UserDisplayNameRule
from univention.scim.server.domain.rules.evaluate import RuleEvaluator


class RuleLoader:
    """
    Loads and configures rules for different resource types.

    This class is responsible for creating rule evaluators with
    the appropriate rules for each resource type.
    """

    @staticmethod
    def get_user_rule_evaluator() -> RuleEvaluator:
        """
        Get a rule evaluator for users.

        Returns:
            A rule evaluator with rules for User resources
        """
        logger.debug("Creating rule evaluator for users")

        evaluator = RuleEvaluator()

        # Add user-specific rules
        evaluator.add_rule(UserDisplayNameRule())

        return evaluator

    @staticmethod
    def get_group_rule_evaluator() -> RuleEvaluator:
        """
        Get a rule evaluator for groups.

        Returns:
            A rule evaluator with rules for Group resources
        """
        logger.debug("Creating rule evaluator for groups")

        evaluator = RuleEvaluator()

        # Add group-specific rules
        # None yet

        return evaluator
