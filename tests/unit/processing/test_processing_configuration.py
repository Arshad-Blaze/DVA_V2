import pytest
import polars as pl

from dav_platform.core.contracts import (
    AggregationConfig,
    AggregationStrategy,
    CalculationConfig,
    CanonicalDataset,
    CanonicalMetadata,
    OperationContext,
    ProcessingConfig,
)
from dav_platform.processing.configuration import build_config


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
class TestBuildConfig:
    def test_default_config_no_args(self):
        config = build_config()

        assert isinstance(config, ProcessingConfig)
        assert config.group_columns == []
        assert config.aggregation_configs == []
        assert config.calculation_configs == []
        assert config.chunk_size == 10_000
        assert config.streaming is True

    def test_explicit_group_columns(self):
        config = build_config(group_columns=["store", "upc"])

        assert config.group_columns == ["store", "upc"]

    def test_dataset_auto_detection(self):
        dataset = _make_dataset()
        config = build_config(dataset=dataset)

        detected = config.group_columns
        assert "store" in detected
        assert "upc" in detected

    def test_dataset_auto_detection_ignores_non_groupable(self):
        df = pl.DataFrame({
            "store": ["S1"],
            "units": [10],
            "custom_field": ["x"],
        })
        dataset = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store", "units", "custom_field"],
            dataframe=df,
        )
        config = build_config(dataset=dataset)

        assert "store" in config.group_columns
        assert "custom_field" not in config.group_columns

    def test_with_operation_context(self):
        ctx = OperationContext(
            options={
                "group_columns": ["brand", "department"],
                "chunk_size": 500,
                "streaming": False,
            }
        )
        config = build_config(context=ctx)

        assert config.group_columns == ["brand", "department"]
        assert config.chunk_size == 500
        assert config.streaming is False

    def test_priority_explicit_over_context(self):
        ctx = OperationContext(
            options={"group_columns": ["brand"]}
        )
        config = build_config(
            group_columns=["store", "upc"], context=ctx
        )

        assert config.group_columns == ["store", "upc"]

    def test_priority_context_over_dataset(self):
        dataset = _make_dataset()
        ctx = OperationContext(
            options={"group_columns": ["brand"]}
        )
        config = build_config(dataset=dataset, context=ctx)

        assert config.group_columns == ["brand"]

    def test_explicit_aggregations_used(self):
        aggs = [
            AggregationConfig(
                column="units",
                strategy=AggregationStrategy.SUM,
                alias="total",
            )
        ]
        config = build_config(aggregations=aggs)

        assert len(config.aggregation_configs) == 1
        assert config.aggregation_configs[0].column == "units"

    def test_context_aggregations_used(self):
        aggs = [
            AggregationConfig(
                column="price",
                strategy=AggregationStrategy.MEAN,
                alias="avg_price",
            )
        ]
        ctx = OperationContext(options={"aggregation_configs": aggs})
        config = build_config(context=ctx)

        assert len(config.aggregation_configs) == 1
        assert config.aggregation_configs[0].alias == "avg_price"

    def test_explicit_calculations_used(self):
        calcs = [
            CalculationConfig(
                name="revenue",
                columns=["units", "price"],
                operation="sum",
                alias="revenue",
            )
        ]
        config = build_config(calculations=calcs)

        assert len(config.calculation_configs) == 1
        assert config.calculation_configs[0].name == "revenue"

    def test_context_calculations_used(self):
        calcs = [
            CalculationConfig(
                name="ratio_calc",
                columns=["units", "price"],
                operation="ratio",
            )
        ]
        ctx = OperationContext(options={"calculation_configs": calcs})
        config = build_config(context=ctx)

        assert len(config.calculation_configs) == 1

    def test_chunk_size_default(self):
        config = build_config()
        assert config.chunk_size == 10_000

    def test_chunk_size_from_context(self):
        ctx = OperationContext(options={"chunk_size": 2500})
        config = build_config(context=ctx)
        assert config.chunk_size == 2500

    def test_chunk_size_explicit_over_context(self):
        ctx = OperationContext(options={"chunk_size": 2500})
        config = build_config(chunk_size=500, context=ctx)
        assert config.chunk_size == 500
