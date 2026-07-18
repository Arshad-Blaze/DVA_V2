"""Validation Layer — Exceptions."""


class ValidationEngineError(Exception):
    """Base error for validation operations."""


class RuleExecutionError(ValidationEngineError):
    """A validation rule failed during execution."""


class ConfigurationError(ValidationEngineError):
    """Invalid validation configuration."""


class RuleNotFoundError(ValidationEngineError):
    """Requested validation rule not found in registry."""


class ValidationError(ValidationEngineError):
    """Validation logic error."""


class InputError(ValidationEngineError):
    """Invalid input to validation layer."""
