import pytest
import polars as pl

from dav_platform.core.contracts import (
    AggregationConfig,
    AggregationResult,
    AggregationStrategy,
    CanonicalDataset,
    CanonicalMetadata,
)
from dav_platform.processing.aggregator import Aggregator


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


# ---------------------------------------------------------------------------
# TestAggregator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAggregator:
    def test_aggregate_groupby_store_sum_units(self):
        dataset = _make_dataset()
        aggregator = Aggregator()
        configs = [
            AggregationConfig(
                column="units",
                strategy=AggregationStrategy.SUM,
                alias="total_units",
            )
        ]

        result = aggregator.aggregate(
            dataset, group_columns=["store"], aggregations=configs
        )

        assert isinstance(result, AggregationResult)
        assert result.row_count == 3
        assert result.data.height == 3
        assert "total_units" in result.data.columns

        s1 = result.data.filter(pl.col("store") == "S1")
        assert s1["total_units"][0] == 30

        s2 = result.data.filter(pl.col("store") == "S2")
        assert s2["total_units"][0] == 70

        s3 = result.data.filter(pl.col("store") == "S3")
        assert s3["total_units"][0] == 50

    def test_aggregate_multiple_aggregations(self):
        dataset = _make_dataset()
        aggregator = Aggregator()
        configs = [
            AggregationConfig(
                column="units",
                strategy=AggregationStrategy.SUM,
                alias="total_units",
            ),
            AggregationConfig(
                column="price",
                strategy=AggregationStrategy.MEAN,
                alias="avg_price",
            ),
        ]

        result = aggregator.aggregate(
            dataset, group_columns=["store"], aggregations=configs
        )

        assert result.row_count == 3
        assert "total_units" in result.data.columns
        assert "avg_price" in result.data.columns

        s1 = result.data.filter(pl.col("store") == "S1")
        assert s1["total_units"][0] == 30
        assert s1["avg_price"][0] == pytest.approx(1.5)

    def test_aggregate_missing_column_returns_warning(self):
        dataset = _make_dataset()
        aggregator = Aggregator()
        configs = [
            AggregationConfig(
                column="nonexistent",
                strategy=AggregationStrategy.SUM,
                alias="bad_col",
            )
        ]

        result = aggregator.aggregate(
            dataset, group_columns=["store"], aggregations=configs
        )

        warnings = result.metadata.get("warnings", [])
        assert any("nonexistent" in w for w in warnings)

    def test_aggregate_result_row_count_matches(self):
        dataset = _make_dataset()
        aggregator = Aggregator()
        configs = [
            AggregationConfig(
                column="units", strategy=AggregationStrategy.COUNT, alias="cnt"
            )
        ]

        result = aggregator.aggregate(
            dataset, group_columns=["store"], aggregations=configs
        )

        assert result.row_count == result.data.height

    def test_aggregate_input_dataset_not_modified(self):
        dataset = _make_dataset()
        original_data = dataset.dataframe.clone()
        aggregator = Aggregator()
        configs = [
            AggregationConfig(
                column="units", strategy=AggregationStrategy.SUM, alias="total"
            )
        ]

        aggregator.aggregate(
            dataset, group_columns=["store"], aggregations=configs
        )

        assert dataset.dataframe.equals(original_data)


# ---------------------------------------------------------------------------
# TestBuildAggExpr
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBuildAggExpr:
    def _make_aggregator(self):
        return Aggregator()

    def _make_config(self, strategy, alias=None):
        return AggregationConfig(column="units", strategy=strategy, alias=alias)

    def _eval_expr(self, config):
        agg = self._make_aggregator()
        expr = agg._build_agg_expr(config)
        df = pl.DataFrame({"units": [10, 20, 30]})
        return df.select(expr).to_series()[0]

    def test_sum_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.SUM))
        assert result == 60

    def test_mean_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.MEAN))
        assert result == pytest.approx(20.0)

    def test_count_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.COUNT))
        assert result == 3

    def test_min_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.MIN))
        assert result == 10

    def test_max_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.MAX))
        assert result == 30

    def test_first_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.FIRST))
        assert result == 10

    def test_last_strategy(self):
        result = self._eval_expr(self._make_config(AggregationStrategy.LAST))
        assert result == 30

    def test_alias_applied(self):
        agg = self._make_aggregator()
        config = self._make_config(AggregationStrategy.SUM, alias="my_sum")
        expr = agg._build_agg_expr(config)

        df = pl.DataFrame({"units": [5, 10]})
        result_df = df.select(expr)
        assert "my_sum" in result_df.columns
        assert result_df["my_sum"][0] == 15
