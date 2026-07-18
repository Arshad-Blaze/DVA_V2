"""Tests for execution planning."""

import pytest

from dav_platform.core.contracts import (
    BusinessGoal,
    ExecutionStep,
    ProcessingMode,
)
from dav_platform.requirements.execution_plan import (
    build_execution_plan,
    format_plan,
)


class TestBuildExecutionPlan:
    def test_review_plan(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="review")
        assert len(plan) > 0
        assert plan[0].action == "load"
        assert all(isinstance(s, ExecutionStep) for s in plan)

    def test_aggregate_report_plan(self):
        plan = build_execution_plan(ProcessingMode.AGGREGATE_ONLY, workflow="aggregate_report")
        actions = [s.action for s in plan]
        assert "aggregate" in actions
        assert "load" in actions

    def test_aggregate_calculate_plan(self):
        plan = build_execution_plan(
            ProcessingMode.AGGREGATE_AND_CALCULATE,
            workflow="aggregate_calculate_report",
        )
        actions = [s.action for s in plan]
        assert "aggregate" in actions
        assert "calculate" in actions
        assert "report" in actions

    def test_validate_plan(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="validate")
        actions = [s.action for s in plan]
        assert "validate_schema" in actions
        assert "validate_data" in actions

    def test_migrate_plan(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="migrate")
        actions = [s.action for s in plan]
        assert "transform" in actions
        assert "export" in actions

    def test_compare_plan(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="compare")
        actions = [s.action for s in plan]
        assert "load_baseline" in actions
        assert "load_comparison" in actions
        assert "compare" in actions

    def test_report_plan(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="report")
        actions = [s.action for s in plan]
        assert "report" in actions

    def test_steps_numbered(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="review")
        for i, step in enumerate(plan, 1):
            assert step.step_number == i

    def test_steps_have_layer(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="review")
        for step in plan:
            assert step.layer == "operation"


class TestFormatPlan:
    def test_format(self):
        plan = build_execution_plan(ProcessingMode.RAW_REVIEW, workflow="review")
        formatted = format_plan(plan)
        assert "load:" in formatted
        assert "[required]" in formatted or "[optional]" in formatted
