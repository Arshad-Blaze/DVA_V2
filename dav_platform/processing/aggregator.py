"""Aggregation Engine for DVA Platform V2.

Performs computations ONLY — no validation, no business decisions.
Uses vectorized polars operations for all aggregations.
"""

import time
from typing import List

import polars as pl

from dav_platform.core.contracts import (
    AggregationConfig,
    AggregationResult,
    AggregationStrategy,
    CanonicalDataset,
)


_STRATEGY_MAP = {
    AggregationStrategy.SUM: lambda col: pl.col(col).sum(),
    AggregationStrategy.MEAN: lambda col: pl.col(col).mean(),
    AggregationStrategy.COUNT: lambda col: pl.col(col).count(),
    AggregationStrategy.MIN: lambda col: pl.col(col).min(),
    AggregationStrategy.MAX: lambda col: pl.col(col).max(),
    AggregationStrategy.FIRST: lambda col: pl.col(col).first(),
    AggregationStrategy.LAST: lambda col: pl.col(col).last(),
}


class Aggregator:
    """Reusable aggregation engine operating on canonical data."""

    def aggregate(
        self,
        dataset: CanonicalDataset,
        group_columns: List[str],
        aggregations: List[AggregationConfig],
    ) -> AggregationResult:
        """Aggregate CanonicalDataset by group_columns using aggregations.

        - Validates group_columns exist in dataset.canonical_columns
        - Uses polars group_by + agg for vectorized execution
        - Returns AggregationResult with aggregated DataFrame
        - Never modifies input dataset
        """
        start = time.perf_counter()

        warnings = self._validate_columns(dataset, group_columns, aggregations)

        valid_columns = set(dataset.canonical_columns)
        valid_group_cols = [c for c in group_columns if c in valid_columns]
        valid_aggs = [cfg for cfg in aggregations if cfg.column in valid_columns]

        if not valid_group_cols or not valid_aggs:
            return AggregationResult(
                data=pl.DataFrame(),
                group_columns=group_columns,
                aggregations=aggregations,
                row_count=0,
                elapsed_seconds=time.perf_counter() - start,
                metadata={"warnings": warnings},
            )

        if dataset.dataframe is None or dataset.dataframe.is_empty():
            return AggregationResult(
                data=pl.DataFrame(),
                group_columns=group_columns,
                aggregations=aggregations,
                row_count=0,
                elapsed_seconds=time.perf_counter() - start,
                metadata={"warnings": warnings},
            )

        agg_exprs = [self._build_agg_expr(cfg) for cfg in valid_aggs]
        result_df = (
            dataset.dataframe
            .group_by(valid_group_cols)
            .agg(agg_exprs)
        )

        elapsed = time.perf_counter() - start

        return AggregationResult(
            data=result_df,
            group_columns=group_columns,
            aggregations=aggregations,
            row_count=result_df.height,
            elapsed_seconds=elapsed,
            metadata={"warnings": warnings},
        )

    def _build_agg_expr(self, config: AggregationConfig) -> pl.Expr:
        """Build a polars aggregation expression from AggregationConfig."""
        builder = _STRATEGY_MAP.get(config.strategy)
        if builder is None:
            raise ValueError(f"Unsupported aggregation strategy: {config.strategy}")

        expr = builder(config.column)

        alias = config.alias
        if alias:
            expr = expr.alias(alias)

        return expr

    def _validate_columns(
        self,
        dataset: CanonicalDataset,
        group_columns: List[str],
        aggregations: List[AggregationConfig],
    ) -> List[str]:
        """Check that all referenced columns exist. Return warnings for missing."""
        warnings: List[str] = []
        valid_columns = set(dataset.canonical_columns)

        for col_name in group_columns:
            if col_name not in valid_columns:
                warnings.append(
                    f"Group column '{col_name}' not found in canonical columns"
                )

        for cfg in aggregations:
            if cfg.column not in valid_columns:
                warnings.append(
                    f"Aggregation column '{cfg.column}' not found in canonical columns"
                )

        return warnings
