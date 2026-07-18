"""Validation Layer — Business Rule Engine.

Evaluates correctness of computed business results.
Performs NO aggregation, NO calculation, NO report generation.
"""

from dav_platform.validation.engine import ValidationEngine
from dav_platform.validation.exceptions import (
    ConfigurationError,
    InputError,
    RuleExecutionError,
    ValidationError,
    ValidationEngineError,
)
from dav_platform.validation.metadata import MetadataCollector
from dav_platform.validation.report import ValidationReportBuilder
from dav_platform.validation.rules import BaseValidationRule, RuleRegistry, get_registry, register_rule
from dav_platform.validation.statistics import ValidationStatisticsEngine
from dav_platform.validation.validators import (
    DifferencePercentageCheck,
    DuplicateDetection,
    MissingEntity,
    NullRequiredFields,
    ToleranceCheck,
    UnexpectedEntity,
    ValueRangeCheck,
)

__all__ = [
    "ValidationEngine",
    "BaseValidationRule",
    "RuleRegistry",
    "get_registry",
    "register_rule",
    "ValidationStatisticsEngine",
    "MetadataCollector",
    "ValidationReportBuilder",
    "ValidationEngineError",
    "RuleExecutionError",
    "ConfigurationError",
    "ValidationError",
    "InputError",
    "NullRequiredFields",
    "DuplicateDetection",
    "MissingEntity",
    "UnexpectedEntity",
    "ValueRangeCheck",
    "ToleranceCheck",
    "DifferencePercentageCheck",
]
