"""Tests — Validation Layer: Rules & Registry."""

import pytest
from dav_platform.core.contracts import ValidationIssue, ValidationRule, ValidationSeverity
from dav_platform.validation.rules import (
    BaseValidationRule,
    RuleRegistry,
    get_registry,
    register_rule,
)
import polars as pl


class TestRuleRegistry:
    def test_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_register_custom_rule(self):
        registry = RuleRegistry()

        @registry.register
        class DummyRule(BaseValidationRule):
            RULE_NAME = "dummy_test_rule"

            def evaluate(self, df, context=None):
                return []

        assert "dummy_test_rule" in registry
        assert len(registry) >= 1

    def test_register_non_subclass_raises(self):
        registry = RuleRegistry()
        with pytest.raises(TypeError):
            registry.register(str)

    def test_create_rule(self):
        registry = RuleRegistry()

        @registry.register
        class TestRule(BaseValidationRule):
            RULE_NAME = "test_create"

            def evaluate(self, df, context=None):
                return []

        rule_def = ValidationRule(name="test_create", rule_type="test_create")
        instance = registry.create(rule_def)
        assert isinstance(instance, BaseValidationRule)
        assert instance.name == "test_create"

    def test_create_unknown_rule_raises(self):
        registry = RuleRegistry()
        rule_def = ValidationRule(name="nonexistent")
        with pytest.raises(ValueError):
            registry.create(rule_def)

    def test_list_rules(self):
        registry = RuleRegistry()

        @registry.register
        class RuleA(BaseValidationRule):
            RULE_NAME = "rule_a"

            def evaluate(self, df, context=None):
                return []

        @registry.register
        class RuleB(BaseValidationRule):
            RULE_NAME = "rule_b"

            def evaluate(self, df, context=None):
                return []

        names = registry.list_rules()
        assert "rule_a" in names
        assert "rule_b" in names

    def test_repr(self):
        rule_def = ValidationRule(name="test", rule_type="test")
        rule = type("R", (BaseValidationRule,), {
            "RULE_NAME": "test",
            "evaluate": lambda self, df, context=None: [],
        })(rule_def)
        assert "test" in repr(rule)


class TestGlobalRegistry:
    def test_global_registry_has_builtin_rules(self):
        registry = get_registry()
        assert "null_required_fields" in registry
        assert "duplicate_detection" in registry
        assert "missing_entity" in registry
        assert "unexpected_entity" in registry
        assert "value_range_check" in registry
        assert "tolerance_check" in registry
        assert "difference_percentage_check" in registry
