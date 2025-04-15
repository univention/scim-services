# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from typing import Generic, TypeVar

from loguru import logger
from scim2_models import Resource

from univention.scim.server.domain.rules.rule import Rule


T = TypeVar("T", bound=Resource)


class RuleEvaluator(Generic[T]):
    """
    Evaluates a set of rules against resources.
    This class is responsible for applying multiple rules in sequence
    to SCIM resources.
    """

    def __init__(self, rules: list[Rule] | None = None):
        """
        Initialize the rule evaluator.
        Args:
            rules: List of rules to evaluate
        """
        self.rules = rules or []

    def add_rule(self, rule: Rule) -> None:
        """
        Add a rule to the evaluator.
        Args:
            rule: The rule to add
        """
        self.rules.append(rule)

    async def evaluate(self, resource: T) -> T:
        """
        Evaluate all rules against a resource.
        Args:
            resource: The resource to evaluate
        Returns:
            The transformed resource after applying all rules
        Raises:
            ValueError: If any rule fails
        """
        logger.debug(f"Evaluating rules for resource {resource.id}")
        result = resource
        for rule in self.rules:
            try:
                result = await rule.apply(result)
            except ValueError as e:
                logger.error(f"Rule {rule.get_name()} failed for resource {resource.id}: {e}")
                raise
        return result
