"""Integration tests for Canonical → Requirement pipeline."""

import pytest

import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.core.contracts import (
    CandidateMapping,
    CanonicalDataset,
    CanonicalMetadata,
    DiscoveryResult,
    FileType,
    OperationContext,
    ProcessingMode,
)
from dav_platform.requirements.engine import RequirementLayer


def _make_discovery_result(columns=None, has_quantity=True):
    """Create a DiscoveryResult for testing."""
    if columns is None:
        columns = ["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"]

    candidates_store = []
    candidates_upc = []
    candidates_units = []
    candidates_price = []

    for c in columns:
        upper = c.upper()
        if "STORE" in upper:
            candidates_store.append(CandidateMapping(
                physical_column=c, confidence=0.9
            ))
        if "UPC" in upper:
            candidates_upc.append(CandidateMapping(
                physical_column=c, confidence=0.9
            ))
        if "UNIT" in upper or "QUANTITY" in upper:
            candidates_units.append(CandidateMapping(
                physical_column=c, confidence=0.8
            ))
        if "PRICE" in upper or "SALE" in upper:
            candidates_price.append(CandidateMapping(
                physical_column=c, confidence=0.8
            ))

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
    """Create test data."""
    if columns is None:
        columns = ["STORE_NUM", "UPC_CODE", "UNITS", "PRICE"]
    return pl.DataFrame({
        "STORE_NUM": ["1001", "1002", "1003"],
        "UPC_CODE": ["123456", "789012", "345678"],
        "UNITS": ["10", "20", "30"],
        "PRICE": ["9.99", "19.99", "29.99"],
    })


class TestCanonicalToRequirementPipeline:
    def test_full_pipeline_aggregate_and_calculate(self):
        """Test complete pipeline: Discovery → Canonical → Requirement."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        assert dataset is not None
        assert dataset.metadata is not None
        assert len(dataset.canonical_columns) > 0

        req_layer = RequirementLayer()
        ctx = req_layer.process(dataset=dataset)

        assert isinstance(ctx, OperationContext)
        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert ctx.session_id is not None
        assert "file_path" in ctx.metadata
        assert "canonical_columns" in ctx.metadata
        assert "quantity_column" in ctx.metadata

    def test_pipeline_aggregate_only(self):
        """Test pipeline with no quantity → AGGREGATE_ONLY."""
        result = _make_discovery_result(has_quantity=False)
        data = _make_data(columns=["STORE_NUM", "UPC_CODE", "PRICE"])

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        ctx = req_layer.process(dataset=dataset)

        assert ctx.mode in (ProcessingMode.AGGREGATE_ONLY, ProcessingMode.RAW_REVIEW)

    def test_pipeline_raw_review(self):
        """Test pipeline with no groupable columns → RAW_REVIEW."""
        result = _make_discovery_result(columns=["UPC_CODE", "DESCRIPTION"])
        data = pl.DataFrame({
            "UPC_CODE": ["123456", "789012"],
            "DESCRIPTION": ["Widget A", "Widget B"],
        })

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        ctx = req_layer.process(dataset=dataset)

        assert ctx.mode == ProcessingMode.RAW_REVIEW

    def test_pipeline_no_physical_leakage(self):
        """Verify no physical column names leak into business metadata."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        ctx = req_layer.process(dataset=dataset)

        # Physical names must not appear in business-critical fields
        assert ctx.metadata["quantity_column"] != "UNITS"
        assert ctx.metadata["quantity_column"] != "STORE_NUM"
        for col in ctx.metadata["canonical_columns"]:
            assert col in ("store", "upc", "quantity", "price", "description",
                           "brand", "category", "department", "date", "uom", "region", "division"), \
                f"Non-canonical column: {col}"

    def test_pipeline_explicit_mode_override(self):
        """Test user can override suggested mode."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        ctx = req_layer.process(
            dataset=dataset,
            mode=ProcessingMode.RAW_REVIEW,
        )

        assert ctx.mode == ProcessingMode.RAW_REVIEW

    def test_pipeline_with_options(self):
        """Test pipeline with user options."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        opts = {"group_by": "store", "sort": "price_desc"}
        ctx = req_layer.process(dataset=dataset, options=opts)

        assert ctx.options == opts

    def test_pipeline_unavailable_mode_falls_back(self):
        """Test that requesting an unavailable mode falls back to RAW_REVIEW."""
        result = _make_discovery_result(columns=["UPC_CODE", "DESCRIPTION"])
        data = pl.DataFrame({
            "UPC_CODE": ["123456"],
            "DESCRIPTION": ["Widget"],
        })

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        ctx = req_layer.process(
            dataset=dataset,
            mode=ProcessingMode.AGGREGATE_AND_CALCULATE,
        )

        assert ctx.mode == ProcessingMode.RAW_REVIEW

    def test_pipeline_available_modes(self):
        """Test getting available modes from pipeline."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        modes = req_layer.get_available_modes(dataset)

        assert ProcessingMode.RAW_REVIEW in modes
        assert ProcessingMode.AGGREGATE_ONLY in modes
        assert ProcessingMode.AGGREGATE_AND_CALCULATE in modes

    def test_pipeline_data_readiness(self):
        """Test data readiness check through pipeline."""
        result = _make_discovery_result()
        data = _make_data()

        canonical_engine = CanonicalEngine()
        dataset = canonical_engine.transform(result, data=data)

        req_layer = RequirementLayer()
        issues = req_layer.check_readiness(dataset)

        assert issues == []
