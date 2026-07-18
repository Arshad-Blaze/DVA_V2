import pytest
import polars as pl

from dav_platform.core.contracts import (
    CalculationConfig,
    CalculationResult,
    CanonicalDataset,
    CanonicalMetadata,
)
from dav_platform.processing.calculator import (
    Calculator,
    _op_avg,
    _op_count,
    _op_difference,
    _op_max,
    _op_min,
    _op_pct_change,
    _op_ratio,
    _op_sum,
)


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


def _config(name, columns, operation, alias=None):
    return CalculationConfig(
        name=name, columns=columns, operation=operation, alias=alias
    )


# ---------------------------------------------------------------------------
# TestCalculator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculator:
    def test_calculate_sum(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [_config("total", ["units", "price"], "sum", "row_total")]

        result = calc.calculate(dataset, configs)

        assert isinstance(result, CalculationResult)
        assert "row_total" in result.data.columns
        assert result.row_count == 5
        row0_total = result.data["row_total"][0]
        assert row0_total == pytest.approx(11.0)

    def test_calculate_difference(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [_config("diff", ["units", "price"], "difference", "units_minus_price")]

        result = calc.calculate(dataset, configs)

        assert "units_minus_price" in result.data.columns
        assert result.data["units_minus_price"][0] == pytest.approx(9.0)

    def test_calculate_ratio(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [_config("ratio", ["units", "price"], "ratio", "units_per_price")]

        result = calc.calculate(dataset, configs)

        assert "units_per_price" in result.data.columns
        assert result.data["units_per_price"][0] == pytest.approx(10.0)

    def test_calculate_ratio_divide_by_zero(self):
        df = pl.DataFrame({
            "store": ["S1"],
            "upc": ["U1"],
            "units": [10],
            "price": [0.0],
        })
        dataset = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store", "upc", "units", "price"],
            dataframe=df,
        )
        calc = Calculator()
        configs = [_config("ratio", ["units", "price"], "ratio", "r")]

        result = calc.calculate(dataset, configs)

        assert result.data["r"][0] is None

    def test_calculate_avg(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [_config("avg", ["units", "price"], "avg", "avg_val")]

        result = calc.calculate(dataset, configs)

        assert "avg_val" in result.data.columns
        assert result.data["avg_val"][0] == pytest.approx(5.5)

    def test_calculate_pct_change(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [
            _config("pct", ["units", "price"], "pct_change", "pct_chg")
        ]

        result = calc.calculate(dataset, configs)

        assert "pct_chg" in result.data.columns
        expected = ((10.0 - 1.0) / 1.0) * 100
        assert result.data["pct_chg"][0] == pytest.approx(expected)

    def test_new_columns_are_added(self):
        dataset = _make_dataset()
        original_cols = set(dataset.dataframe.columns)
        calc = Calculator()
        configs = [_config("tot", ["units", "price"], "sum", "row_sum")]

        result = calc.calculate(dataset, configs)

        assert "row_sum" in result.data.columns
        assert "row_sum" not in original_cols

    def test_missing_column_returns_error(self):
        dataset = _make_dataset()
        calc = Calculator()
        configs = [_config("bad", ["units", "nonexistent"], "sum", "out")]

        result = calc.calculate(dataset, configs)

        assert len(result.errors) > 0


# ---------------------------------------------------------------------------
# TestCalculationOperations
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCalculationOperations:
    def _df(self):
        return pl.DataFrame({
            "a": [10.0, 20.0, 30.0],
            "b": [1.0, 2.0, 3.0],
        })

    def test_op_sum(self):
        cfg = _config("s", ["a", "b"], "sum", "total")
        result = _op_sum(self._df(), cfg)
        assert "total" in result.columns
        assert result["total"][0] == pytest.approx(11.0)
        assert result["total"][2] == pytest.approx(33.0)

    def test_op_difference(self):
        cfg = _config("d", ["a", "b"], "difference", "diff")
        result = _op_difference(self._df(), cfg)
        assert "diff" in result.columns
        assert result["diff"][0] == pytest.approx(9.0)

    def test_op_ratio(self):
        cfg = _config("r", ["a", "b"], "ratio", "ratio_col")
        result = _op_ratio(self._df(), cfg)
        assert "ratio_col" in result.columns
        assert result["ratio_col"][0] == pytest.approx(10.0)

    def test_op_ratio_zero_division(self):
        df = pl.DataFrame({"a": [5.0], "b": [0.0]})
        cfg = _config("r", ["a", "b"], "ratio", "r")
        result = _op_ratio(df, cfg)
        assert result["r"][0] is None

    def test_op_avg(self):
        cfg = _config("av", ["a", "b"], "avg", "avg_val")
        result = _op_avg(self._df(), cfg)
        assert "avg_val" in result.columns
        assert result["avg_val"][0] == pytest.approx(5.5)

    def test_op_min(self):
        cfg = _config("mn", ["a", "b"], "min", "min_val")
        result = _op_min(self._df(), cfg)
        assert "min_val" in result.columns
        assert result["min_val"][0] == pytest.approx(1.0)

    def test_op_max(self):
        cfg = _config("mx", ["a", "b"], "max", "max_val")
        result = _op_max(self._df(), cfg)
        assert "max_val" in result.columns
        assert result["max_val"][0] == pytest.approx(10.0)

    def test_op_count(self):
        cfg = _config("ct", ["a", "b"], "count", "count_val")
        result = _op_count(self._df(), cfg)
        assert "count_val" in result.columns
        assert result["count_val"][0] == 2

    def test_op_pct_change(self):
        cfg = _config("pc", ["a", "b"], "pct_change", "pct")
        result = _op_pct_change(self._df(), cfg)
        assert "pct" in result.columns
        expected = ((10.0 - 1.0) / 1.0) * 100
        assert result["pct"][0] == pytest.approx(expected)
