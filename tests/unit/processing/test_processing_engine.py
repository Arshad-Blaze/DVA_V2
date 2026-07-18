import pytest
import polars as pl

from dav_platform.core.contracts import (
    AggregationConfig,
    AggregationResult,
    AggregationStrategy,
    CalculationConfig,
    CalculationResult,
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingConfig,
    ProcessingResult,
    ProcessingStatistics,
)
from dav_platform.processing.engine import ProcessingEngine


def _make_dataset() -> CanonicalDataset:
    df = pl.DataFrame({
        "store": ["S1", "S1", "S2", "S2", "S3"],
        "upc": ["U1", "U2", "U1", "U2", "U1"],
        "units": [10, 20, 30, 40, 50],
        "price": [1.0, 2.0, 3.0, 4.0, 5.0],
    })
    return CanonicalDataset(
        file_path="/test.csv",
        canonical_columns=["store", "upc", "units", "price"],
        metadata=CanonicalMetadata(
            total_rows=5,
            quantity_column="units",
            quantity_type="units",
        ),
        dataframe=df,
    )


@pytest.mark.unit
class TestProcessingEngine:
    def test_process_aggregation_calculation_stats(self):
        dataset = _make_dataset()
        config = ProcessingConfig(
            group_columns=["store"],
            aggregation_configs=[
                AggregationConfig(
                    column="units",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            calculation_configs=[
                CalculationConfig(
                    name="price_times",
                    columns=["units", "price"],
                    operation="sum",
                    alias="units_plus_price",
                ),
            ],
            compute_statistics=True,
        )
        engine = ProcessingEngine()

        result = engine.process(dataset, config=config)

        assert isinstance(result, ProcessingResult)
        assert result.row_count == 3
        assert "total_units" in result.df.columns
        assert "steps" in result.metadata
        assert len(result.metadata["steps"]) >= 2

    def test_aggregate_returns_aggregation_result(self):
        dataset = _make_dataset()
        config = ProcessingConfig(
            group_columns=["store"],
            aggregation_configs=[
                AggregationConfig(
                    column="units",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
        )
        engine = ProcessingEngine()

        result = engine.aggregate(dataset, config)

        assert isinstance(result, AggregationResult)
        assert result.row_count == 3
        assert "total_units" in result.data.columns

    def test_calculate_returns_calculation_result(self):
        dataset = _make_dataset()
        config = ProcessingConfig(
            calculation_configs=[
                CalculationConfig(
                    name="diff",
                    columns=["units", "price"],
                    operation="difference",
                    alias="units_minus_price",
                ),
            ],
        )
        engine = ProcessingEngine()

        result = engine.calculate(dataset, config)

        assert isinstance(result, CalculationResult)
        assert result.row_count == 5
        assert "units_minus_price" in result.data.columns

    def test_compute_statistics_returns_processing_statistics(self):
        dataset = _make_dataset()
        engine = ProcessingEngine()

        stats = engine.compute_statistics(dataset)

        assert isinstance(stats, ProcessingStatistics)
        assert stats.total_rows == 5

    def test_process_with_streaming_config(self):
        dataset = _make_dataset()
        config = ProcessingConfig(
            group_columns=["store"],
            aggregation_configs=[
                AggregationConfig(
                    column="units",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            chunk_size=2,
            streaming=True,
            compute_statistics=False,
        )
        engine = ProcessingEngine()

        result = engine.process(dataset, config=config)

        assert isinstance(result, ProcessingResult)
        assert result.row_count == 3

    def test_process_input_dataset_not_modified(self):
        dataset = _make_dataset()
        original_df = dataset.dataframe.clone()
        config = ProcessingConfig(
            group_columns=["store"],
            aggregation_configs=[
                AggregationConfig(
                    column="units",
                    strategy=AggregationStrategy.SUM,
                    alias="total_units",
                ),
            ],
            compute_statistics=False,
        )
        engine = ProcessingEngine()

        engine.process(dataset, config=config)

        assert dataset.dataframe.equals(original_df)

    def test_process_empty_dataset_returns_error(self):
        df = pl.DataFrame({
            "store": [],
            "upc": [],
            "units": [],
            "price": [],
        })
        dataset = CanonicalDataset(
            file_path="/empty.csv",
            canonical_columns=["store", "upc", "units", "price"],
            dataframe=df,
        )
        engine = ProcessingEngine()

        result = engine.process(dataset)

        assert len(result.errors) > 0

    def test_process_builds_config_from_context(self):
        from dav_platform.core.contracts import OperationContext

        dataset = _make_dataset()
        ctx = OperationContext(
            options={
                "group_columns": ["store"],
                "aggregation_configs": [
                    AggregationConfig(
                        column="units",
                        strategy=AggregationStrategy.SUM,
                        alias="total_units",
                    ),
                ],
                "chunk_size": 500,
            }
        )
        engine = ProcessingEngine()

        result = engine.process(dataset, context=ctx)

        assert isinstance(result, ProcessingResult)
        assert result.row_count == 3
