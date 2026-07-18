"""Execution Planning.

Builds step-by-step execution plans for the Operation Layer.
"""

from typing import List, Optional

from dav_platform.core.contracts import (
    BusinessGoal,
    ExecutionStep,
    ProcessingMode,
)


def build_execution_plan(
    mode: ProcessingMode,
    goal: Optional[BusinessGoal] = None,
    workflow: str = "",
) -> List[ExecutionStep]:
    """Build an execution plan based on mode and goal.

    Args:
        mode: Selected processing mode
        goal: Detected business goal
        workflow: Recommended workflow name

    Returns:
        List of ExecutionStep objects
    """
    if workflow == "validate":
        return _plan_validate()
    if workflow == "migrate":
        return _plan_migrate()
    if workflow == "compare":
        return _plan_compare()
    if workflow == "report":
        return _plan_report()
    if workflow == "aggregate_calculate_report":
        return _plan_aggregate_calculate_report()
    if workflow == "aggregate_report":
        return _plan_aggregate_report()

    return _plan_review()


def _plan_review() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "preview", "Generate data preview", required=True, layer="operation"),
        ExecutionStep(3, "summary", "Generate summary statistics", required=False, layer="operation"),
    ]


def _plan_aggregate_report() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "validate", "Validate data completeness", required=True, layer="operation"),
        ExecutionStep(3, "aggregate", "Aggregate data by groupable columns", required=True, layer="operation"),
        ExecutionStep(4, "summary", "Generate summary statistics", required=False, layer="operation"),
        ExecutionStep(5, "report", "Generate aggregation report", required=False, layer="operation"),
    ]


def _plan_aggregate_calculate_report() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "validate", "Validate data completeness", required=True, layer="operation"),
        ExecutionStep(3, "aggregate", "Aggregate data by groupable columns", required=True, layer="operation"),
        ExecutionStep(4, "calculate", "Calculate quantities and totals", required=True, layer="operation"),
        ExecutionStep(5, "summary", "Generate summary statistics", required=False, layer="operation"),
        ExecutionStep(6, "report", "Generate calculation report", required=False, layer="operation"),
    ]


def _plan_validate() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "validate_schema", "Validate schema against rules", required=True, layer="operation"),
        ExecutionStep(3, "validate_data", "Validate data quality", required=True, layer="operation"),
        ExecutionStep(4, "report", "Generate validation report", required=True, layer="operation"),
    ]


def _plan_migrate() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "validate", "Validate migration readiness", required=True, layer="operation"),
        ExecutionStep(3, "transform", "Apply target transformations", required=True, layer="operation"),
        ExecutionStep(4, "validate_output", "Validate transformed output", required=True, layer="operation"),
        ExecutionStep(5, "export", "Export to target format", required=True, layer="operation"),
    ]


def _plan_compare() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load_baseline", "Load baseline dataset", required=True, layer="operation"),
        ExecutionStep(2, "load_comparison", "Load comparison dataset", required=True, layer="operation"),
        ExecutionStep(3, "align", "Align schemas between datasets", required=True, layer="operation"),
        ExecutionStep(4, "compare", "Compare datasets", required=True, layer="operation"),
        ExecutionStep(5, "report", "Generate comparison report", required=True, layer="operation"),
    ]


def _plan_report() -> List[ExecutionStep]:
    return [
        ExecutionStep(1, "load", "Load canonical dataset", required=True, layer="operation"),
        ExecutionStep(2, "aggregate", "Aggregate data", required=True, layer="operation"),
        ExecutionStep(3, "calculate", "Calculate metrics", required=False, layer="operation"),
        ExecutionStep(4, "report", "Generate report", required=True, layer="operation"),
        ExecutionStep(5, "export", "Export report", required=False, layer="operation"),
    ]


def format_plan(plan: List[ExecutionStep]) -> str:
    """Format execution plan as readable string."""
    lines = []
    for step in plan:
        req = "[required]" if step.required else "[optional]"
        lines.append(f"  {step.step_number}. {step.action}: {step.description} {req}")
    return "\n".join(lines)
