"""Validation Layer — Business Rule Engine.

Strategy Pattern: each rule is a pluggable strategy.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    ValidationIssue,
    ValidationRule,
)


class BaseValidationRule(ABC):
    """Base class for all validation rules.

    Each rule is a strategy that evaluates a DataFrame
    and returns a list of ValidationIssue objects.
    """

    def __init__(self, rule_def: ValidationRule):
        self.rule_def = rule_def
        self.name = rule_def.name
        self.rule_type = rule_def.rule_type
        self.severity = rule_def.severity
        self.enabled = rule_def.enabled
        self.parameters = rule_def.parameters

    @abstractmethod
    def evaluate(self, df: pl.DataFrame, context: Optional[Dict[str, Any]] = None) -> List[ValidationIssue]:
        """Evaluate this rule against the DataFrame.

        Args:
            df: The DataFrame to validate.
            context: Optional context dict (expected values, tolerances, etc.).

        Returns:
            List of ValidationIssue objects (empty if rule passes).
        """
        ...

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} type={self.rule_type!r}>"


class RuleRegistry:
    """Registry of pluggable validation rules.

    Follows Strategy + Registry pattern.
    New rules register themselves here.
    """

    def __init__(self):
        self._rules: Dict[str, type] = {}

    def register(self, rule_class: type) -> type:
        """Register a rule class. Can be used as a decorator."""
        if not issubclass(rule_class, BaseValidationRule):
            raise TypeError(f"{rule_class} must subclass BaseValidationRule")
        rule_name = getattr(rule_class, 'RULE_NAME', rule_class.__name__)
        self._rules[rule_name] = rule_class
        return rule_class

    def get(self, rule_name: str) -> Optional[type]:
        return self._rules.get(rule_name)

    def create(self, rule_def: ValidationRule) -> BaseValidationRule:
        """Instantiate a rule from a ValidationRule definition."""
        cls = self._rules.get(rule_def.name)
        if cls is None:
            cls = self._rules.get(rule_def.rule_type)
        if cls is None:
            raise ValueError(f"Unknown rule: {rule_def.name} (type={rule_def.rule_type})")
        return cls(rule_def)

    def list_rules(self) -> List[str]:
        return list(self._rules.keys())

    def __len__(self):
        return len(self._rules)

    def __contains__(self, name: str):
        return name in self._rules


_registry = RuleRegistry()


def get_registry() -> RuleRegistry:
    return _registry


def register_rule(rule_class: type) -> type:
    """Register a rule class in the global registry."""
    _registry.register(rule_class)
    return rule_class
