"""Requirement Layer — Main orchestrator.

Translates user intent into a fully-planned OperationContext.
Consumes CanonicalDataset, produces OperationContext with:
- Business goal
- Capability matrix
- Execution plan
- Recommendations
- Validation results
"""

from typing import Any, Dict, Optional

from dav_platform.core.contracts import (
    BusinessGoal,
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
    check_data_readiness,
    validate_mode,
)
from dav_platform.requirements.context_builder import build_context
from dav_platform.requirements.business_goal import detect_business_goal
from dav_platform.requirements.capability import detect_capabilities
from dav_platform.requirements.recommendation import recommend
from dav_platform.requirements.execution_plan import build_execution_plan


class RequirementLayer:
    """Planning engine of the platform.

    Determines WHAT should happen, not HOW.
    Operation Layer executes the supplied plan.

    Consumes: CanonicalDataset (from Canonical Layer)
    Produces: OperationContext (for Operation Layer)
    """

    def process(
        self,
        dataset: Optional[CanonicalDataset] = None,
        mode: Optional[ProcessingMode] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> OperationContext:
        """Full requirement processing pipeline.

        1. Detect business goal
        2. Detect capabilities
        3. Determine mode (user-specified or auto-suggested)
        4. Validate mode against dataset
        5. Generate recommendations
        6. Build execution plan
        7. Build OperationContext with all intelligence

        Args:
            dataset: CanonicalDataset from Canonical Layer
            mode: Requested processing mode (auto-suggested if None)
            options: User-specified processing options

        Returns:
            OperationContext for the Operation Layer
        """
        options = options or {}
        user_specified_mode = mode is not None

        # Step 1: Detect business goal
        goal = detect_business_goal(dataset, mode, options)

        # Step 2: Detect capabilities
        capabilities = detect_capabilities(dataset)

        # Step 3: Determine mode
        if mode is None:
            mode = suggest_mode(dataset)
        else:
            mode = select_mode(mode, dataset)

        # Step 4: Validate
        validation = validate_mode(mode, dataset)

        # Step 5: Generate recommendations
        rec = recommend(dataset, capabilities, goal)

        # Override mode with recommended ONLY when user didn't specify
        if not user_specified_mode and rec.confidence > 0.7:
            mode = rec.best_mode

        # Step 6: Build execution plan
        plan = build_execution_plan(mode, goal, rec.best_workflow)

        # Step 7: Build context
        context = build_context(
            mode=mode,
            dataset=dataset,
            options=options,
        )

        # Enhance context with intelligence
        context.business_goal = goal
        context.capability_matrix = capabilities
        context.execution_plan = plan
        context.recommended_workflow = rec.best_workflow
        context.warnings = rec.warnings
        context.confidence = rec.confidence

        # Required/missing inputs
        context.required_inputs = _determine_required_inputs(goal, mode)
        context.missing_inputs = rec.missing_prerequisites

        # Expected outputs
        context.expected_outputs = rec.expected_outputs

        # Attach detailed results to metadata
        context.metadata["validation"] = {
            "passed": validation.passed,
            "issues": validation.issues,
            "warnings": validation.warnings,
        }
        context.metadata["business_goal"] = goal.value
        context.metadata["capability_matrix"] = capabilities.to_dict()
        context.metadata["recommended_workflow"] = rec.best_workflow
        context.metadata["aggregation_strategy"] = rec.aggregation_strategy
        context.metadata["calculation_strategy"] = rec.calculation_strategy
        context.metadata["execution_plan_steps"] = len(plan)
        context.metadata["confidence"] = rec.confidence

        return context

    def get_available_modes(
        self,
        dataset: Optional[CanonicalDataset] = None,
    ) -> list:
        """Get available processing modes."""
        return get_available_modes(dataset)

    def check_readiness(
        self,
        dataset: Optional[CanonicalDataset] = None,
    ) -> list:
        """Check if data is ready for processing."""
        return check_data_readiness(dataset)

    def analyze(
        self,
        dataset: Optional[CanonicalDataset] = None,
    ) -> Dict[str, Any]:
        """Quick analysis without full processing.

        Returns a summary of goals, capabilities, and recommendations.

        Args:
            dataset: CanonicalDataset from Canonical Layer

        Returns:
            Dict with goal, capabilities, recommendation, available_modes
        """
        goal = detect_business_goal(dataset)
        capabilities = detect_capabilities(dataset)
        rec = recommend(dataset, capabilities, goal)
        modes = get_available_modes(dataset)

        return {
            "business_goal": goal,
            "capabilities": capabilities,
            "recommendation": rec,
            "available_modes": modes,
        }


def _determine_required_inputs(
    goal: Optional[BusinessGoal],
    mode: ProcessingMode,
) -> list:
    """Determine required inputs based on goal and mode."""
    inputs = ["canonical_dataset"]

    if mode in (ProcessingMode.AGGREGATE_ONLY, ProcessingMode.AGGREGATE_AND_CALCULATE):
        inputs.append("groupable_columns")

    if mode == ProcessingMode.AGGREGATE_AND_CALCULATE:
        inputs.append("quantity_column")

    if goal == BusinessGoal.COMPARISON:
        inputs.append("comparison_dataset")

    if goal == BusinessGoal.MIGRATION:
        inputs.append("target_schema")

    return inputs
