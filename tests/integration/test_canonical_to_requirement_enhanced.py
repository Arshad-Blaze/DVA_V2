"""Integration tests for enhanced Requirement Layer (Sprint 4B)."""

import pytest

import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.core.contracts import (
    BusinessGoal,
    CandidateMapping,
    CapabilityMatrix,
    DiscoveryResult,
    ExecutionStep,
    FileType,
    OperationContext,
    ProcessingMode,
)
from dav_platform.requirements.engine import RequirementLayer
from dav_platform.requirements.execution_plan import format_plan


def _make_discovery_result(columns=None, has_quantity=True):
    if columns is None:
        columns = ["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"]

    candidates_store = []
    candidates_upc = []
    candidates_units = []
    candidates_price = []

    for c in columns:
        upper = c.upper()
        if "STORE" in upper:
            candidates_store.append(CandidateMapping(physical_column=c, confidence=0.9))
        if "UPC" in upper:
            candidates_upc.append(CandidateMapping(physical_column=c, confidence=0.9))
        if "UNIT" in upper:
            candidates_units.append(CandidateMapping(physical_column=c, confidence=0.8))
        if "PRICE" in upper:
            candidates_price.append(CandidateMapping(physical_column=c, confidence=0.8))

    return DiscoveryResult(
        file_path="/test.csv",
        file_type=FileType.DELIMITED,
        delimiter="|",
        has_header=True,
        encoding="utf-8",
        columns=columns,
        candidate_store=candidates_store,
        candidate_upc=candidates_upc,
        candidate_units=candidates_units if has_quantity else [],
        candidate_price=candidates_price,
        confidence=0.85,
    )


def _make_data(columns=None):
    if columns is None:
        columns = ["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"]
    return pl.DataFrame({
        "STORE_NUM": ["1001", "1002", "1003"],
        "UPC_CODE": ["123456", "789012", "345678"],
        "UNITS": ["10", "20", "30"],
        "PRICE": ["9.99", "19.99", "29.99"],
    })


class TestEnhancedPipeline:
    def test_full_enhanced_pipeline(self):
        """Test complete enhanced pipeline with all Sprint 4B features."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        layer = RequirementLayer()
        ctx = layer.process(dataset=canonical)

        # Core fields
        assert isinstance(ctx, OperationContext)
        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE

        # Sprint 4B fields
        assert ctx.business_goal is not None
        assert isinstance(ctx.capability_matrix, CapabilityMatrix)
        assert ctx.capability_matrix.can_aggregate is True
        assert ctx.capability_matrix.can_calculate is True
        assert len(ctx.execution_plan) > 0
        assert ctx.recommended_workflow == "aggregate_calculate_report"
        assert ctx.confidence > 0.8

    def test_execution_plan_steps(self):
        """Verify execution plan has proper steps."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        assert all(isinstance(s, ExecutionStep) for s in ctx.execution_plan)
        # Plan should have load, validate, aggregate, calculate, report
        actions = [s.action for s in ctx.execution_plan]
        assert "load" in actions
        assert "aggregate" in actions
        assert "calculate" in actions

    def test_format_plan(self):
        """Verify plan formatting works."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        formatted = format_plan(ctx.execution_plan)
        assert isinstance(formatted, str)
        assert "load" in formatted

    def test_explicit_mode_respected(self):
        """User-specified mode should override recommendation."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(
            dataset=canonical,
            mode=ProcessingMode.RAW_REVIEW,
        )

        assert ctx.mode == ProcessingMode.RAW_REVIEW
        # But should still have intelligence
        assert ctx.business_goal is not None
        assert ctx.capability_matrix is not None

    def test_no_data_capabilities(self):
        """Empty dataset should have limited capabilities."""
        result = _make_discovery_result(columns=["UPC_CODE", "DESCRIPTION"])
        data = pl.DataFrame({"UPC_CODE": ["123"], "DESCRIPTION": ["Widget"]})

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        # Should fall back to review
        assert ctx.mode == ProcessingMode.RAW_REVIEW
        assert ctx.capability_matrix.can_aggregate is False

    def test_metadata_enhanced(self):
        """Verify enhanced metadata fields are populated."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        assert "business_goal" in ctx.metadata
        assert "capability_matrix" in ctx.metadata
        assert "recommended_workflow" in ctx.metadata
        assert "execution_plan_steps" in ctx.metadata
        assert "confidence" in ctx.metadata

    def test_analyze_quick(self):
        """Test the quick analyze method."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        layer = RequirementLayer()
        analysis = layer.analyze(dataset=canonical)

        assert "business_goal" in analysis
        assert "capabilities" in analysis
        assert "recommendation" in analysis
        assert "available_modes" in analysis

    def test_required_inputs(self):
        """Verify required inputs are populated."""
        result = _make_discovery_result()
        data = _make_data()

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        assert "canonical_dataset" in ctx.required_inputs
        assert "groupable_columns" in ctx.required_inputs
        assert "quantity_column" in ctx.required_inputs

    def test_warnings_populated(self):
        """Verify warnings are populated for edge cases."""
        result = _make_discovery_result(columns=["UPC_CODE"], has_quantity=False)
        data = pl.DataFrame({"UPC_CODE": ["123"]})

        canonical = CanonicalEngine().transform(result, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        assert len(ctx.warnings) > 0  # no groupable columns warning

    def test_pipeline_end_to_end(self):
        """Full end-to-end: Discovery → Canonical → Requirement → OperationContext."""
        # Discovery
        result = _make_discovery_result()
        data = _make_data()

        # Canonical
        canonical = CanonicalEngine().transform(result, data=data)
        assert canonical.metadata is not None

        # Requirement
        ctx = RequirementLayer().process(dataset=canonical)
        assert isinstance(ctx, OperationContext)

        # Verify Operation Layer receives a complete plan
        assert ctx.execution_plan is not None
        assert len(ctx.execution_plan) > 0
        assert ctx.business_goal is not None
        assert ctx.capability_matrix is not None
