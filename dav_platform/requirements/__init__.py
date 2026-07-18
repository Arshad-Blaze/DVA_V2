"""Requirement Layer — User intent translation.

Translates user intent into OperationContext for the Operation Layer.
"""

from dav_platform.requirements.engine import RequirementLayer
from dav_platform.requirements.mode_selector import (
    get_available_modes,
    select_mode,
    suggest_mode,
)
from dav_platform.requirements.validator import (
    ValidationResult,
    check_data_readiness,
    validate_mode,
)
from dav_platform.requirements.context_builder import (
    build_context,
    build_session_id,
    extract_metadata,
)

__all__ = [
    "RequirementLayer",
    "get_available_modes",
    "select_mode",
    "suggest_mode",
    "ValidationResult",
    "check_data_readiness",
    "validate_mode",
    "build_context",
    "build_session_id",
    "extract_metadata",
]
