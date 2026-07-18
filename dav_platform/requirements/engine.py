"""Requirement Layer — Main orchestrator.

Translates user intent into OperationContext for the Operation Layer.
Consumes CanonicalDataset, produces OperationContext.
"""

from typing import Any, Dict, Optional

from dav_platform.core.contracts import (
    CanonicalDataset,
    OperationContext,
    ProcessingMode,
)
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
from dav_platform.requirements.context_builder import build_context


class RequirementLayer:
    """Orchestrates requirement processing.

    Translates user intent (mode selection) into a structured
    OperationContext that the Operation Layer consumes.

    Consumes: CanonicalDataset (from Canonical Layer)
    Produces: OperationContext (for Operation Layer)
    """

    def process(
        self,
        dataset: Optional[CanonicalDataset] = None,
        mode: Optional[ProcessingMode] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> OperationContext:
        """Process user intent and build OperationContext.

        Pipeline:
        1. Suggest mode if not provided
        2. Validate mode availability
        3. Validate mode against dataset
        4. Build context

        Args:
            dataset: CanonicalDataset from Canonical Layer
            mode: Requested processing mode (auto-suggested if None)
            options: User-specified processing options

        Returns:
            OperationContext for the Operation Layer
        """
        # Step 1: Determine mode
        if mode is None:
            mode = suggest_mode(dataset)
        else:
            mode = select_mode(mode, dataset)

        # Step 2: Validate mode against dataset
        validation = validate_mode(mode, dataset)

        # Step 3: Build context
        context = build_context(
            mode=mode,
            dataset=dataset,
            options=options,
        )

        # Attach validation results to context metadata
        context.metadata["validation"] = {
            "passed": validation.passed,
            "issues": validation.issues,
            "warnings": validation.warnings,
        }

        return context

    def get_available_modes(
        self,
        dataset: Optional[CanonicalDataset] = None,
    ) -> list:
        """Get available processing modes for this dataset.

        Args:
            dataset: CanonicalDataset from Canonical Layer

        Returns:
            List of available ProcessingMode values
        """
        return get_available_modes(dataset)

    def check_readiness(
        self,
        dataset: Optional[CanonicalDataset] = None,
    ) -> list:
        """Check if data is ready for processing.

        Args:
            dataset: CanonicalDataset from Canonical Layer

        Returns:
            List of readiness issues (empty if ready)
        """
        return check_data_readiness(dataset)
