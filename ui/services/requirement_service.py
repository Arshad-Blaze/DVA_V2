"""Requirement service — Analysis Planner (Sprint 5).

Manages planning state: business goals, capability matrix,
execution plan, readiness, and confirmation.
Never builds OperationContext — only visualizes and collects choices.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field, asdict

from dav_platform.core.contracts import (
    ProcessingMode,
    BusinessGoal,
    CapabilityMatrix,
    ExecutionStep,
    OperationContext,
)


BUSINESS_GOALS_DEMO = [
    {"id": "retailer_onboarding", "label": "Retailer Onboarding", "description": "Full onboarding: ingest, validate, and generate reports for a new retailer", "icon": "storefront", "complexity": "High", "mode": ProcessingMode.AGGREGATE_AND_CALCULATE, "goal_enum": BusinessGoal.AGGREGATION},
    {"id": "format_change", "label": "Format Change", "description": "Convert file format without aggregation or calculation", "icon": "swap_horiz", "complexity": "Low", "mode": ProcessingMode.RAW_REVIEW, "goal_enum": BusinessGoal.FORMAT_CHANGE},
    {"id": "migration_validation", "label": "Migration Validation", "description": "Compare source and target datasets to verify data integrity", "icon": "compare_arrows", "complexity": "Medium", "mode": ProcessingMode.AGGREGATE_ONLY, "goal_enum": BusinessGoal.MIGRATION},
    {"id": "raw_data_review", "label": "Raw Data Review", "description": "Preview raw data without any transformation", "icon": "visibility", "complexity": "Low", "mode": ProcessingMode.RAW_REVIEW, "goal_enum": BusinessGoal.RAW_REVIEW},
    {"id": "aggregate_only", "label": "Aggregate Only", "description": "Aggregate data by store, item, or department", "icon": "functions", "complexity": "Low", "mode": ProcessingMode.AGGREGATE_ONLY, "goal_enum": BusinessGoal.AGGREGATION},
    {"id": "aggregate_calculate", "label": "Aggregate + Calculate", "description": "Aggregate and calculate derived metrics", "icon": "calculate", "complexity": "Medium", "mode": ProcessingMode.AGGREGATE_AND_CALCULATE, "goal_enum": BusinessGoal.CALCULATION},
    {"id": "store_validation", "label": "Store Validation", "description": "Validate store-level data completeness and accuracy", "icon": "verified", "complexity": "Medium", "mode": ProcessingMode.AGGREGATE_ONLY, "goal_enum": BusinessGoal.VALIDATION},
    {"id": "item_validation", "label": "Item Validation", "description": "Validate item-level data quality", "icon": "inventory_2", "complexity": "Medium", "mode": ProcessingMode.AGGREGATE_ONLY, "goal_enum": BusinessGoal.VALIDATION},
    {"id": "custom_analysis", "label": "Custom Analysis", "description": "Define custom reporting and analysis requirements", "icon": "analytics", "complexity": "Variable", "mode": ProcessingMode.AGGREGATE_AND_CALCULATE, "goal_enum": BusinessGoal.REPORTING},
]

WORKFLOWS_DEMO = {
    "aggregate_calculate": {
        "workflow": "Aggregate by store and item, calculate sales metrics, validate results, generate reports",
        "confidence": 0.95,
        "reason": "All required fields mapped, quantity resolved, dataset has 1250 rows across 45 stores",
        "alternatives": ["Aggregate Only", "Store Validation", "Custom Analysis"],
    },
    "aggregate_only": {
        "workflow": "Aggregate data by store, department, and category",
        "confidence": 0.90,
        "reason": "Required fields present, quantity mapped to units",
        "alternatives": ["Aggregate + Calculate", "Store Validation"],
    },
    "raw_data_review": {
        "workflow": "Review raw data without aggregation or transformation",
        "confidence": 0.98,
        "reason": "Data already in readable format",
        "alternatives": ["Format Change", "Custom Analysis"],
    },
    "store_validation": {
        "workflow": "Validate store-level data across all 45 stores for completeness and accuracy",
        "confidence": 0.92,
        "reason": "Store and sales fields mapped, 45 stores detected",
        "alternatives": ["Item Validation", "Aggregate Only"],
    },
    "item_validation": {
        "workflow": "Validate item-level data for 892 unique UPCs across all departments",
        "confidence": 0.88,
        "reason": "UPC and description mapped, 892 unique items detected",
        "alternatives": ["Store Validation", "Aggregate + Calculate"],
    },
    "retailer_onboarding": {
        "workflow": "Full onboarding: aggregate, validate, report across all 45 stores and 12 categories",
        "confidence": 0.93,
        "reason": "Complete mapping, all required fields present, comprehensive dataset",
        "alternatives": ["Aggregate + Calculate", "Store Validation", "Custom Analysis"],
    },
    "migration_validation": {
        "workflow": "Compare dataset against reference to verify migration integrity",
        "confidence": 0.85,
        "reason": "Reference dataset required but not provided",
        "alternatives": ["Format Change", "Raw Data Review"],
    },
    "format_change": {
        "workflow": "Convert file to required output format without transformation",
        "confidence": 0.97,
        "reason": "No aggregation or calculation needed",
        "alternatives": ["Raw Data Review", "Custom Analysis"],
    },
    "custom_analysis": {
        "workflow": "User-defined analysis and reporting pipeline",
        "confidence": 0.80,
        "reason": "Custom goals require additional configuration",
        "alternatives": ["Aggregate + Calculate", "Retailer Onboarding"],
    },
}

# Default recommendation when no goal selected
DEFAULT_RECOMMENDATION = {
    "workflow": "Aggregate by store and item, calculate sales metrics, validate results, generate reports",
    "confidence": 0.95,
    "reason": "Dataset has complete mapping with 9 mapped columns across 45 stores — optimal for standard retail analysis",
    "alternatives": ["Aggregate Only", "Store Validation", "Custom Analysis"],
}

EXECUTION_PLANS_DEMO = {
    "aggregate_calculate": [
        ExecutionStep(1, "Load Data", "Load canonical dataset from mapped source", True, "processing"),
        ExecutionStep(2, "Aggregate", "Aggregate by store, item, and date dimensions", True, "processing"),
        ExecutionStep(3, "Calculate", "Calculate total sales, average price, item count metrics", True, "processing"),
        ExecutionStep(4, "Validate", "Validate aggregated results against business rules", True, "validation"),
        ExecutionStep(5, "Generate Reports", "Generate store, item, and summary reports", True, "reports"),
        ExecutionStep(6, "Export", "Export results to Excel, CSV, and Parquet", True, "reports"),
    ],
    "aggregate_only": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "Aggregate", "Aggregate by selected dimensions", True, "processing"),
        ExecutionStep(3, "Generate Reports", "Generate summary reports", True, "reports"),
        ExecutionStep(4, "Export", "Export results", True, "reports"),
    ],
    "raw_data_review": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "Generate Preview", "Generate raw data preview", True, "reports"),
        ExecutionStep(3, "Export", "Export raw data", False, "reports"),
    ],
    "store_validation": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "Aggregate", "Aggregate by store", True, "processing"),
        ExecutionStep(3, "Validate", "Validate store-level completeness", True, "validation"),
        ExecutionStep(4, "Generate Reports", "Generate store validation report", True, "reports"),
        ExecutionStep(5, "Export", "Export results", True, "reports"),
    ],
    "item_validation": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "Aggregate", "Aggregate by item", True, "processing"),
        ExecutionStep(3, "Validate", "Validate item-level data quality", True, "validation"),
        ExecutionStep(4, "Generate Reports", "Generate item validation report", True, "reports"),
        ExecutionStep(5, "Export", "Export results", True, "reports"),
    ],
    "retailer_onboarding": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "Aggregate", "Aggregate by store, item, department, category", True, "processing"),
        ExecutionStep(3, "Calculate", "Calculate all retail metrics", True, "processing"),
        ExecutionStep(4, "Validate", "Run full validation suite", True, "validation"),
        ExecutionStep(5, "Generate Reports", "Generate complete onboarding report package", True, "reports"),
        ExecutionStep(6, "Export", "Export all outputs", True, "reports"),
    ],
    "migration_validation": [
        ExecutionStep(1, "Load Data", "Load source dataset", True, "processing"),
        ExecutionStep(2, "Load Reference", "Load reference/target dataset", True, "processing"),
        ExecutionStep(3, "Compare", "Compare source and target datasets", True, "processing"),
        ExecutionStep(4, "Validate", "Validate migration integrity", True, "validation"),
        ExecutionStep(5, "Generate Reports", "Generate migration report", True, "reports"),
        ExecutionStep(6, "Export", "Export comparison results", True, "reports"),
    ],
    "format_change": [
        ExecutionStep(1, "Load Data", "Load dataset", True, "processing"),
        ExecutionStep(2, "Convert", "Convert to target format", True, "processing"),
        ExecutionStep(3, "Export", "Export converted data", True, "reports"),
    ],
    "custom_analysis": [
        ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
        ExecutionStep(2, "User Processing", "Execute user-defined processing steps", True, "processing"),
        ExecutionStep(3, "Generate Reports", "Generate custom reports", True, "reports"),
        ExecutionStep(4, "Export", "Export results", True, "reports"),
    ],
}

DEFAULT_PLAN = [
    ExecutionStep(1, "Load Data", "Load canonical dataset", True, "processing"),
    ExecutionStep(2, "Aggregate", "Aggregate by dimensions", True, "processing"),
    ExecutionStep(3, "Validate", "Validate results", True, "validation"),
    ExecutionStep(4, "Generate Reports", "Generate reports", True, "reports"),
    ExecutionStep(5, "Export", "Export results", True, "reports"),
]

EXPECTED_OUTPUTS_DEMO = {
    "aggregate_calculate": [
        "Store Summary Report (Excel)",
        "Item Summary Report (Excel)",
        "Department Summary Report (Excel)",
        "Category Summary Report (Excel)",
        "Aggregated Dataset (CSV/Parquet)",
        "Execution Summary",
    ],
    "aggregate_only": [
        "Store Summary Report (Excel)",
        "Department Summary Report (Excel)",
        "Aggregated Dataset (CSV)",
        "Execution Summary",
    ],
    "raw_data_review": [
        "Raw Data Preview (Excel)",
        "Raw Data Export (CSV)",
    ],
    "store_validation": [
        "Store Validation Report (Excel)",
        "Store Completeness Scores (CSV)",
        "Execution Summary",
    ],
    "item_validation": [
        "Item Validation Report (Excel)",
        "Item Quality Scores (CSV)",
        "Execution Summary",
    ],
    "retailer_onboarding": [
        "Complete Onboarding Package (Excel)",
        "Store Summary Report",
        "Item Summary Report",
        "Validation Report",
        "Business Statistics Report",
        "All Outputs (CSV/Parquet)",
    ],
    "migration_validation": [
        "Migration Comparison Report (Excel)",
        "Differences Export (CSV)",
        "Integrity Score Report",
        "Execution Summary",
    ],
    "format_change": [
        "Converted Dataset (target format)",
        "Conversion Report",
    ],
    "custom_analysis": [
        "Custom Report Package",
        "Analysis Dataset (CSV/Parquet)",
        "Execution Summary",
    ],
}

DEFAULT_OUTPUTS = [
    "Execution Summary",
    "Processed Dataset (CSV)",
]

ESTIMATES_DEMO = {
    "aggregate_calculate": {"runtime": "2-5 min", "complexity": "Medium", "memory": "256 MB", "streaming": True, "report_count": 5, "validation_rules": 12},
    "aggregate_only": {"runtime": "1-2 min", "complexity": "Low", "memory": "128 MB", "streaming": True, "report_count": 3, "validation_rules": 0},
    "raw_data_review": {"runtime": "< 30 sec", "complexity": "Very Low", "memory": "64 MB", "streaming": True, "report_count": 1, "validation_rules": 0},
    "store_validation": {"runtime": "1-3 min", "complexity": "Medium", "memory": "128 MB", "streaming": True, "report_count": 2, "validation_rules": 8},
    "item_validation": {"runtime": "2-4 min", "complexity": "Medium", "memory": "256 MB", "streaming": True, "report_count": 2, "validation_rules": 10},
    "retailer_onboarding": {"runtime": "5-10 min", "complexity": "High", "memory": "512 MB", "streaming": True, "report_count": 6, "validation_rules": 20},
    "migration_validation": {"runtime": "3-7 min", "complexity": "High", "memory": "512 MB", "streaming": False, "report_count": 3, "validation_rules": 15},
    "format_change": {"runtime": "< 1 min", "complexity": "Low", "memory": "64 MB", "streaming": True, "report_count": 1, "validation_rules": 0},
    "custom_analysis": {"runtime": "Variable", "complexity": "Variable", "memory": "Variable", "streaming": True, "report_count": 3, "validation_rules": 5},
}

DEFAULT_ESTIMATES = {"runtime": "1-2 min", "complexity": "Low", "memory": "128 MB", "streaming": True, "report_count": 2, "validation_rules": 0}

READINESS_DEMO = {
    "project_ready": True,
    "connection_ready": True,
    "detection_ready": True,
    "canonical_ready": True,
    "preview_approved": True,
    "requirement_complete": False,
}

WARNINGS_DEMO = {
    "migration_validation": [
        {"problem": "Reference dataset required", "impact": "Migration validation cannot proceed without target data", "recommendation": "Upload or connect reference dataset", "severity": "error"},
    ],
    "custom_analysis": [
        {"problem": "Custom processing not pre-configured", "impact": "Additional setup steps required before execution", "recommendation": "Define custom processing rules", "severity": "warning"},
    ],
    "default": [],
}

MISSING_INPUTS_DEMO: Dict[str, List[Dict[str, str]]] = {
    "migration_validation": [
        {"input": "Reference Dataset", "detail": "Target dataset for comparison is not connected", "navigate": "connection"},
    ],
    "custom_analysis": [
        {"input": "Custom Processing Rules", "detail": "Define rules for custom analysis pipeline", "navigate": ""},
    ],
    "default": [],
}

CAPABILITY_DESCRIPTIONS = {
    "can_aggregate": {"label": "Aggregation", "icon": "functions"},
    "can_calculate": {"label": "Calculations", "icon": "calculate"},
    "can_compare": {"label": "Comparison", "icon": "compare_arrows"},
    "can_validate": {"label": "Validation", "icon": "verified"},
    "can_migrate": {"label": "Migration", "icon": "luggage"},
    "can_report": {"label": "Reporting", "icon": "assessment"},
    "can_review": {"label": "Raw Data Review", "icon": "visibility"},
}

GOAL_CAPABILITIES = {
    "retailer_onboarding": CapabilityMatrix(can_aggregate=True, can_calculate=True, can_validate=True, can_report=True, can_review=False, can_compare=False, can_migrate=False),
    "format_change": CapabilityMatrix(can_aggregate=False, can_calculate=False, can_validate=False, can_report=True, can_review=True, can_compare=False, can_migrate=True),
    "migration_validation": CapabilityMatrix(can_aggregate=False, can_calculate=False, can_validate=True, can_report=True, can_review=True, can_compare=True, can_migrate=True),
    "raw_data_review": CapabilityMatrix(can_aggregate=False, can_calculate=False, can_validate=False, can_report=True, can_review=True, can_compare=False, can_migrate=False),
    "aggregate_only": CapabilityMatrix(can_aggregate=True, can_calculate=False, can_validate=False, can_report=True, can_review=False, can_compare=False, can_migrate=False),
    "aggregate_calculate": CapabilityMatrix(can_aggregate=True, can_calculate=True, can_validate=True, can_report=True, can_review=False, can_compare=False, can_migrate=False),
    "store_validation": CapabilityMatrix(can_aggregate=True, can_calculate=False, can_validate=True, can_report=True, can_review=False, can_compare=False, can_migrate=False),
    "item_validation": CapabilityMatrix(can_aggregate=True, can_calculate=False, can_validate=True, can_report=True, can_review=False, can_compare=False, can_migrate=False),
    "custom_analysis": CapabilityMatrix(can_aggregate=True, can_calculate=True, can_validate=True, can_report=True, can_review=True, can_compare=True, can_migrate=True),
}

GOAL_MODES = {
    g["id"]: g["mode"] for g in BUSINESS_GOALS_DEMO
}


class RequirementService:
    """Manages Analysis Planner state.

    Never builds OperationContext — visualizes and collects user choices only.
    """

    def __init__(self, context=None):
        self._context = context
        self._selected_goal_id: Optional[str] = None
        self._confirmed: bool = False
        self._recommendation_accepted: bool = False
        self._on_change: Optional[Callable] = None
        self._goals = list(BUSINESS_GOALS_DEMO)

    # ── Goal Management ─────────────────────────────────────

    @property
    def available_goals(self) -> List[Dict[str, Any]]:
        return list(self._goals)

    @property
    def selected_goal_id(self) -> Optional[str]:
        return self._selected_goal_id

    def select_goal(self, goal_id: str) -> None:
        goal_ids = {g["id"] for g in self._goals}
        if goal_id in goal_ids:
            self._selected_goal_id = goal_id
            self._confirmed = False
            self._recommendation_accepted = False
            self._notify()

    def clear_goal(self) -> None:
        self._selected_goal_id = None
        self._confirmed = False
        self._recommendation_accepted = False
        self._notify()

    # ── Recommendation ──────────────────────────────────────

    @property
    def recommendation(self) -> Dict[str, Any]:
        if self._selected_goal_id and self._selected_goal_id in WORKFLOWS_DEMO:
            return dict(WORKFLOWS_DEMO[self._selected_goal_id])
        return dict(DEFAULT_RECOMMENDATION)

    @property
    def selected_goal(self) -> Optional[Dict[str, Any]]:
        for g in self._goals:
            if g["id"] == self._selected_goal_id:
                return dict(g)
        return None

    @property
    def recommendation_accepted(self) -> bool:
        return self._recommendation_accepted

    def accept_recommendation(self) -> None:
        if self._selected_goal_id:
            self._recommendation_accepted = True
            self._notify()

    # ── Capability Matrix ───────────────────────────────────

    @property
    def capability_matrix(self) -> CapabilityMatrix:
        if self._selected_goal_id and self._selected_goal_id in GOAL_CAPABILITIES:
            return GOAL_CAPABILITIES[self._selected_goal_id]
        return CapabilityMatrix()

    @property
    def capability_descriptions(self) -> Dict[str, Dict[str, str]]:
        return dict(CAPABILITY_DESCRIPTIONS)

    # ── Execution Plan ──────────────────────────────────────

    @property
    def execution_plan(self) -> List[ExecutionStep]:
        if self._selected_goal_id and self._selected_goal_id in EXECUTION_PLANS_DEMO:
            return list(EXECUTION_PLANS_DEMO[self._selected_goal_id])
        return list(DEFAULT_PLAN)

    @property
    def execution_plan_count(self) -> int:
        return len(self.execution_plan)

    # ── Outputs ─────────────────────────────────────────────

    @property
    def expected_outputs(self) -> List[str]:
        if self._selected_goal_id and self._selected_goal_id in EXPECTED_OUTPUTS_DEMO:
            return list(EXPECTED_OUTPUTS_DEMO[self._selected_goal_id])
        return list(DEFAULT_OUTPUTS)

    # ── Estimates ───────────────────────────────────────────

    @property
    def execution_estimates(self) -> Dict[str, Any]:
        if self._selected_goal_id and self._selected_goal_id in ESTIMATES_DEMO:
            return dict(ESTIMATES_DEMO[self._selected_goal_id])
        return dict(DEFAULT_ESTIMATES)

    # ── Warnings ────────────────────────────────────────────

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        if self._selected_goal_id and self._selected_goal_id in WARNINGS_DEMO:
            return [dict(w) for w in WARNINGS_DEMO[self._selected_goal_id]]
        return [dict(w) for w in WARNINGS_DEMO.get("default", [])]

    # ── Missing Inputs ──────────────────────────────────────

    @property
    def missing_inputs(self) -> List[Dict[str, str]]:
        if self._selected_goal_id and self._selected_goal_id in MISSING_INPUTS_DEMO:
            return [dict(m) for m in MISSING_INPUTS_DEMO[self._selected_goal_id]]
        return [dict(m) for m in MISSING_INPUTS_DEMO.get("default", [])]

    # ── Readiness ───────────────────────────────────────────

    @property
    def readiness(self) -> Dict[str, bool]:
        r = dict(READINESS_DEMO)
        r["requirement_complete"] = self._confirmed
        return r

    @property
    def overall_readiness(self) -> str:
        r = self.readiness
        all_ready = all(r.values())
        any_red = not r.get("preview_approved", False)
        if all_ready:
            return "Ready"
        elif any_red:
            return "Review Required"
        return "Almost Ready"

    # ── Confirmation ────────────────────────────────────────

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    @property
    def can_confirm(self) -> bool:
        return (
            self._selected_goal_id is not None
            and self._recommendation_accepted
            and len(self.missing_inputs) == 0
        )

    def confirm_plan(self) -> None:
        if self.can_confirm:
            self._confirmed = True
            self._notify()

    def reset(self) -> None:
        self._selected_goal_id = None
        self._confirmed = False
        self._recommendation_accepted = False
        self._notify()

    # ── OperationContext (display only) ────────────────────

    def get_operation_context(self) -> OperationContext:
        goal = self.selected_goal
        return OperationContext(
            mode=GOAL_MODES.get(self._selected_goal_id, ProcessingMode.AGGREGATE_ONLY),
            business_goal=goal["goal_enum"] if goal else None,
            capability_matrix=self.capability_matrix,
            execution_plan=self.execution_plan,
            recommended_workflow=self.recommendation.get("workflow", ""),
            required_inputs=[m["input"] for m in self.missing_inputs],
            missing_inputs=[m["input"] for m in self.missing_inputs],
            expected_outputs=self.expected_outputs,
            warnings=[w["problem"] for w in self.warnings],
            confidence=self.recommendation.get("confidence", 0.0),
        )

    # ── Events ──────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
