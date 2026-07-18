"""Calculation Engine for DVA Platform V2.

Performs computations ONLY — no validation, no business decisions.
All calculations operate on canonical fields using vectorized polars operations.
"""

import logging
import time
from typing import List, Optional

import polars as pl

from dav_platform.core.contracts import (
    CalculationConfig,
    CalculationResult,
    CanonicalDataset,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Operation Implementations (module-level functions)
# ============================================================================


def _op_sum(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Sum of specified columns."""
    alias = config.alias or f"{config.name}_{config.operation}"
    numeric_cols = [pl.col(c).cast(pl.Float64) for c in config.columns]
    return df.with_columns(
        pl.concat_list(numeric_cols).list.sum().alias(alias)
    )


def _op_difference(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Difference between first two columns (col1 - col2)."""
    alias = config.alias or f"{config.name}_{config.operation}"
    col1 = config.columns[0]
    col2 = config.columns[1]
    return df.with_columns(
        (pl.col(col1).cast(pl.Float64) - pl.col(col2).cast(pl.Float64)).alias(alias)
    )


def _op_ratio(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Ratio of first two columns (col1 / col2) with divide-by-zero protection."""
    alias = config.alias or f"{config.name}_{config.operation}"
    col1 = config.columns[0]
    col2 = config.columns[1]
    return df.with_columns(
        pl.when(pl.col(col2).cast(pl.Float64) != 0)
        .then(pl.col(col1).cast(pl.Float64) / pl.col(col2).cast(pl.Float64))
        .otherwise(None)
        .alias(alias)
    )


def _op_avg(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Average of specified columns."""
    alias = config.alias or f"{config.name}_{config.operation}"
    numeric_cols = [pl.col(c).cast(pl.Float64) for c in config.columns]
    return df.with_columns(
        pl.concat_list(numeric_cols).list.mean().alias(alias)
    )


def _op_min(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Row-wise min of specified columns."""
    alias = config.alias or f"{config.name}_{config.operation}"
    numeric_cols = [pl.col(c).cast(pl.Float64) for c in config.columns]
    return df.with_columns(
        pl.concat_list(numeric_cols).list.min().alias(alias)
    )


def _op_max(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Row-wise max of specified columns."""
    alias = config.alias or f"{config.name}_{config.operation}"
    numeric_cols = [pl.col(c).cast(pl.Float64) for c in config.columns]
    return df.with_columns(
        pl.concat_list(numeric_cols).list.max().alias(alias)
    )


def _op_count(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Count non-null values across specified columns."""
    alias = config.alias or f"{config.name}_{config.operation}"
    null_checks = [pl.col(c).is_not_null().cast(pl.Int64) for c in config.columns]
    return df.with_columns(
        pl.concat_list(null_checks).list.sum().alias(alias)
    )


def _op_pct_change(df: pl.DataFrame, config: CalculationConfig) -> pl.DataFrame:
    """Percentage change between first two columns: ((col1 - col2) / col2) * 100."""
    alias = config.alias or f"{config.name}_{config.operation}"
    col1 = config.columns[0]
    col2 = config.columns[1]
    return df.with_columns(
        pl.when(pl.col(col2).cast(pl.Float64) != 0)
        .then(
            ((pl.col(col1).cast(pl.Float64) - pl.col(col2).cast(pl.Float64))
             / pl.col(col2).cast(pl.Float64))
            * 100
        )
        .otherwise(None)
        .alias(alias)
    )


# ============================================================================
# Calculator Class
# ============================================================================


class Calculator:
    """Reusable calculation engine operating on canonical data."""

    OPERATIONS = {
        "sum": _op_sum,
        "difference": _op_difference,
        "ratio": _op_ratio,
        "avg": _op_avg,
        "min": _op_min,
        "max": _op_max,
        "count": _op_count,
        "pct_change": _op_pct_change,
    }

    def calculate(
        self,
        dataset: CanonicalDataset,
        calculations: List[CalculationConfig],
    ) -> CalculationResult:
        """Execute calculations on CanonicalDataset.

        Each CalculationConfig specifies columns and operation.
        Adds new columns with alias names.
        Returns CalculationResult with enriched DataFrame.
        Never modifies input dataset.
        """
        start = time.time()

        if dataset.df is None or dataset.df.is_empty():
            return CalculationResult(
                data=pl.DataFrame(),
                calculations=calculations,
                row_count=0,
                elapsed_seconds=0.0,
                metadata={"status": "empty_dataset"},
            )

        warnings: List[str] = []
        errors: List[str] = []
        df = dataset.df.clone()
        executed_configs: List[CalculationConfig] = []

        for config in calculations:
            calc_warnings = self._validate_calculation(dataset, config)
            if calc_warnings:
                warnings.extend(calc_warnings)

            if config.operation not in self.OPERATIONS:
                errors.append(
                    f"Unknown operation '{config.operation}' for calculation '{config.name}'"
                )
                continue

            if not config.columns:
                errors.append(
                    f"No columns specified for calculation '{config.name}'"
                )
                continue

            missing = [c for c in config.columns if c not in df.columns]
            if missing:
                errors.append(
                    f"Columns {missing} not found for calculation '{config.name}'"
                )
                continue

            try:
                df = self._execute_calculation(df, config)
                executed_configs.append(config)
            except Exception as e:
                errors.append(
                    f"Calculation '{config.name}' failed: {e}"
                )

        elapsed = time.time() - start

        return CalculationResult(
            data=df,
            calculations=executed_configs,
            row_count=df.height,
            elapsed_seconds=elapsed,
            metadata={
                "input_columns": dataset.canonical_columns,
                "operations_executed": len(executed_configs),
                "warnings": warnings,
            },
            errors=errors,
        )

    def _execute_calculation(
        self, df: pl.DataFrame, config: CalculationConfig
    ) -> pl.DataFrame:
        """Execute a single calculation and return new DataFrame with result column."""
        op_func = self.OPERATIONS[config.operation]
        return op_func(df, config)

    def _validate_calculation(
        self, dataset: CanonicalDataset, config: CalculationConfig
    ) -> List[str]:
        """Validate that calculation columns exist. Return warnings."""
        warnings: List[str] = []
        if dataset.df is None:
            return [f"Cannot validate '{config.name}': dataset has no dataframe"]

        for col in config.columns:
            if col not in dataset.df.columns:
                warnings.append(
                    f"Column '{col}' in calculation '{config.name}' "
                    f"not found in dataset columns"
                )
        return warnings
