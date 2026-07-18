"""Integration tests for Requirement → Operation pipeline."""

import pytest

import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.core.contracts import (
    CandidateMapping,
    DiscoveryResult,
    ExecutionState,
    ExecutionResult,
    FileType,
    OperationContext,
    ProcessingMode,
)
from dav_platform.operations.engine import OperationEngine
from dav_platform.operations.dispatcher import clear_handlers, register_handler
from dav_platform.requirements.engine import RequirementLayer


def _make_discovery_result():
    return DiscoveryResult(
        file_path="/test.csv",
        file_type=FileType.DELIMITED,
        delimiter="|",
        has_header=True,
        encoding="utf-8",
        columns=["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"],
        candidate_store=[CandidateMapping(physical_column="STORE_NUM", confidence=0.9)],
        candidate_upc=[CandidateMapping(physical_column="UPC_CODE", confidence=0.9)],
        candidate_units=[CandidateMapping(physical_column="UNITS", confidence=0.8)],
        candidate_price=[CandidateMapping(physical_column="PRICE", confidence=0.8)],
        confidence=0.85,
    )


def _make_data():
    return pl.DataFrame({
        "STORE_NUM": ["1001", "1002", "1003"],
        "UPC_CODE": ["123456", "789012", "345678"],
        "UNITS": ["10", "20", "30"],
        "PRICE": ["9.99", "19.99", "29.99"],
    })


class TestRequirementToOperationPipeline:
    def setup_method(self):
        clear_handlers()

    def teardown_method(self):
        clear_handlers()

    def test_full_pipeline(self):
        """Test complete: Discovery → Canonical → Requirement → Operation."""
        result = _make_discovery_result()
        data = _make_data()

        # Canonical
        canonical = CanonicalEngine().transform(result, data=data)

        # Requirement
        ctx = RequirementLayer().process(dataset=canonical)
        assert ctx.execution_plan is not None

        # Operation — register mock handlers
        executed_actions = []

        def mock_handler(step, dataset=None, context=None, options=None):
            executed_actions.append(step.action)
            return {"action": step.action, "status": "done"}

        for action in ["load", "validate", "preview", "aggregate", "calculate", "summary", "report"]:
            register_handler(action, mock_handler)

        engine = OperationEngine()
        op_result = engine.execute(ctx, dataset=canonical)

        assert isinstance(op_result, ExecutionResult)
        assert op_result.succeeded
        assert op_result.metadata is not None
        assert op_result.metadata.outcome == "success"
        assert len(executed_actions) > 0

    def test_pipeline_raw_review(self):
        """Test RAW_REVIEW workflow through full pipeline."""
        # Use dataset without groupable columns to force RAW_REVIEW
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            delimiter="|",
            has_header=True,
            encoding="utf-8",
            columns=["UPC_CODE", "DESCRIPTION"],
            candidate_upc=[CandidateMapping(physical_column="UPC_CODE", confidence=0.9)],
            confidence=0.85,
        )
        data = pl.DataFrame({
            "UPC_CODE": ["123456", "789012"],
            "DESCRIPTION": ["Widget A", "Widget B"],
        })

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(
            dataset=canonical,
            mode=ProcessingMode.RAW_REVIEW,
        )

        executed = []
        def mock_handler(step, dataset=None, context=None, options=None):
            executed.append(step.action)
            return "ok"

        for action in ["load", "preview", "summary"]:
            register_handler(action, mock_handler)

        engine = OperationEngine()
        op_result = engine.execute(ctx, dataset=canonical)

        assert op_result.succeeded
        assert "load" in executed
        assert "preview" in executed

    def test_pipeline_with_failed_step(self):
        """Test pipeline handles step failures gracefully."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        def good_handler(step, dataset=None, context=None, options=None):
            return "ok"

        def failing_handler(step, dataset=None, context=None, options=None):
            raise RuntimeError("simulated failure")

        register_handler("load", good_handler)
        register_handler("validate", failing_handler)

        engine = OperationEngine()
        op_result = engine.execute(ctx, dataset=canonical)

        # Should have failed steps but overall result exists
        assert isinstance(op_result, ExecutionResult)
        assert op_result.metadata is not None
        assert op_result.metadata.failed_steps > 0

    def test_operation_does_not_modify_context(self):
        """Verify Operation does not modify OperationContext."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        original_mode = ctx.mode
        original_workflow = ctx.recommended_workflow
        original_plan_len = len(ctx.execution_plan)

        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        for action in ["load", "validate", "preview", "aggregate", "calculate", "summary", "report"]:
            register_handler(action, handler)

        engine = OperationEngine()
        engine.execute(ctx, dataset=canonical)

        # Context should be unchanged
        assert ctx.mode == original_mode
        assert ctx.recommended_workflow == original_workflow
        assert len(ctx.execution_plan) == original_plan_len

    def test_operation_logs_complete(self):
        """Verify execution produces complete logs."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        for action in ["load", "validate", "preview", "aggregate", "calculate", "summary", "report"]:
            register_handler(action, handler)

        engine = OperationEngine()
        op_result = engine.execute(ctx, dataset=canonical)

        # Should have logs
        assert len(op_result.logs) > 0
        # Should have execution start and end
        messages = [l.message for l in op_result.logs]
        assert any("started" in m for m in messages)
        assert any("completed" in m for m in messages)

    def test_operation_metadata_complete(self):
        """Verify execution metadata is fully populated."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        def handler(step, dataset=None, context=None, options=None):
            return "ok"

        for action in ["load", "validate", "preview", "aggregate", "calculate", "summary", "report"]:
            register_handler(action, handler)

        engine = OperationEngine()
        op_result = engine.execute(ctx, dataset=canonical)

        meta = op_result.metadata
        assert meta.workflow == ctx.recommended_workflow
        assert meta.total_steps > 0
        assert meta.execution_duration >= 0
        assert meta.outcome in ("success", "partial", "failed", "cancelled")
