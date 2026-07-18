"""Requirement Layer — User intent translation and planning.

Translates user intent into a fully-planned OperationContext.
"""

from dav_platform.requirements.engine import RequirementLayer
from dav_platform.requirements.mode_selector import (
    get_available_modes,
    select_mode,
    suggest_mode,
)
from dav_platform.requirements.validator import (
    ModeValidationResult,
    check_data_readiness,
    validate_mode,
)
from dav_platform.requirements.context_builder import (
    build_context,
    build_session_id,
    extract_metadata,
)
from dav_platform.requirements.business_goal import detect_business_goal
from dav_platform.requirements.capability import detect_capabilities, get_capability_summary
from dav_platform.requirements.recommendation import recommend, Recommendation
from dav_platform.requirements.execution_plan import build_execution_plan, format_plan

__all__ = [
    "RequirementLayer",
    "get_available_modes",
    "select_mode",
    "suggest_mode",
    "ModeValidationResult",
    "check_data_readiness",
    "validate_mode",
    "build_context",
    "build_session_id",
    "extract_metadata",
    "detect_business_goal",
    "detect_capabilities",
    "get_capability_summary",
    "recommend",
    "Recommendation",
    "build_execution_plan",
    "format_plan",
]
