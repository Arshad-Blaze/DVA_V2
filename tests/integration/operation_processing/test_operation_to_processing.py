"""Integration tests for Operation → Processing pipeline."""

import pytest
import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.requirements.engine import RequirementLayer
from dav_platform.operations.engine import OperationEngine
from dav_platform.operations.dispatcher import register_handler, clear_handlers
from dav_platform.processing.engine import ProcessingEngine
from dav_platform.processing.configuration import build_config
from dav_platform.core.contracts import (
    DiscoveryResult,
    FileType,
    CandidateMapping,
    CanonicalDataset,
    CanonicalMetadata,
    OperationContext,
    ProcessingMode,
    AggregationConfig,
    AggregationStrategy,
)


class TestOperationToProcessingPipeline:
    """Integration tests for Operation → Processing pipeline."""

    def setup_method(self):
        clear_handlers()

    def teardown_method(self):
        clear_handlers()

    def _make_discovery(self):
        """Create a minimal DiscoveryResult."""
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

    def _make_data(self):
        """Create a minimal DataFrame."""
        return pl.DataFrame({
            "STORE_NUM": ["1001", "1001", "1002", "1002", "1003"],
            "UPC_CODE": ["123", "456", "789", "012", "345"],
            "UNITS": ["10", "20", "30", "40", "50"],
            "PRICE": ["1.0", "2.0", "3.0", "4.0", "5.0"],
        })

    def _register_mock_handlers(self):
        """Register mock handlers for all required operation actions."""

        def mock_handler(step, dataset=None, context=None, options=None):
            return "ok"

        for action in ["load", "validate", "preview", "aggregate", "calculate", "summary", "report"]:
            register_handler(action, mock_handler)

    def _run_pipeline(self):
        """Run Discovery → Canonical → Requirement → Operation and return canonical dataset."""
        discovery = self._make_discovery()
        data = self._make_data()

        canonical = CanonicalEngine().transform(discovery, data=data)
        ctx = RequirementLayer().process(dataset=canonical)

        self._register_mock_handlers()
        op_result = OperationEngine().execute(ctx, dataset=canonical)
        assert op_result.succeeded

        return canonical

    def test_full_pipeline_aggregation(self):
        """Run full pipeline then ProcessingEngine.process() with aggregation config.

        Group by store, sum units. Verify aggregated data has 3 rows (3 stores).
        """
        canonical = self._run_pipeline()

        config = build_config(
            group_columns=["store"],
            aggregations=[
                AggregationConfig(
                    column="quantity",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            chunk_size=10_000,
            streaming=False,
        )

        engine = ProcessingEngine()
        result = engine.process(dataset=canonical, config=config)

        assert result.row_count > 0
        assert result.row_count == 3
        assert result.errors == []

    def test_full_pipeline_calculation(self):
        """Run full pipeline then ProcessingEngine.calculate() with sum calculation.

        Verify new column is added to the dataset.
        """
        canonical = self._run_pipeline()

        from dav_platform.core.contracts import CalculationConfig, ProcessingConfig

        calc_config = ProcessingConfig(
            calculation_configs=[
                CalculationConfig(
                    name="units_plus_price",
                    columns=["quantity", "price"],
                    operation="sum",
                    alias="units_plus_price",
                ),
            ],
            compute_statistics=False,
        )

        engine = ProcessingEngine()
        result = engine.calculate(dataset=canonical, config=calc_config)

        assert result.row_count == canonical.row_count
        assert "units_plus_price" in result.data.columns
        assert len(result.calculations) == 1

    def test_full_pipeline_statistics(self):
        """Run full pipeline then ProcessingEngine.compute_statistics().

        Verify total_rows == 5 and unique_stores == 3.
        """
        canonical = self._run_pipeline()

        engine = ProcessingEngine()
        stats = engine.compute_statistics(canonical)

        assert stats.total_rows == 5
        assert stats.unique_stores == 3

    def test_pipeline_does_not_modify_dataset(self):
        """Verify CanonicalDataset is unchanged after processing."""
        canonical = self._run_pipeline()

        original_df = canonical.dataframe.clone()
        original_col_count = canonical.column_count
        original_row_count = canonical.row_count

        config = build_config(
            group_columns=["store"],
            aggregations=[
                AggregationConfig(
                    column="quantity",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            chunk_size=10_000,
            streaming=False,
        )

        engine = ProcessingEngine()
        engine.process(dataset=canonical, config=config)

        assert canonical.dataframe.equals(original_df)
        assert canonical.column_count == original_col_count
        assert canonical.row_count == original_row_count

    def test_pipeline_with_streaming_config(self):
        """Create ProcessingConfig with chunk_size=2, streaming=True.

        Run process(). Verify result succeeds.
        """
        canonical = self._run_pipeline()

        from dav_platform.core.contracts import ProcessingConfig

        config = ProcessingConfig(
            group_columns=["store"],
            aggregation_configs=[
                AggregationConfig(
                    column="quantity",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            chunk_size=2,
            streaming=True,
            compute_statistics=False,
        )

        engine = ProcessingEngine()
        result = engine.process(dataset=canonical, config=config)

        assert result.row_count > 0
        assert result.errors == []
