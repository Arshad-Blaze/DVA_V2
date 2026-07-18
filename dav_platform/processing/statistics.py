import time
from typing import Any, Dict, List, Optional

import polars as pl

from dav_platform.core.contracts import CanonicalDataset, ProcessingStatistics


class StatisticsEngine:
    """Generate processing statistics from canonical data."""

    CANONICAL_COLUMNS = ["store", "upc", "category", "brand", "department"]

    def compute(
        self,
        dataset: CanonicalDataset,
        groupable_columns: Optional[List[str]] = None,
    ) -> ProcessingStatistics:
        start = time.time()

        df = dataset.dataframe

        if df is None or df.is_empty():
            return ProcessingStatistics(
                total_rows=0,
                elapsed_seconds=time.time() - start,
            )

        total_rows = df.height

        unique_stores = self._count_uniques(df, "store")
        unique_upcs = self._count_uniques(df, "upc")
        unique_categories = self._count_uniques(df, "category")
        unique_brands = self._count_uniques(df, "brand")
        unique_departments = self._count_uniques(df, "department")

        null_counts = self._count_nulls(df)

        duplicate_count = self._count_duplicates(df)

        column_stats = self._compute_numeric_stats(df)

        elapsed = time.time() - start

        return ProcessingStatistics(
            total_rows=total_rows,
            unique_stores=unique_stores,
            unique_upcs=unique_upcs,
            unique_categories=unique_categories,
            unique_brands=unique_brands,
            unique_departments=unique_departments,
            duplicate_count=duplicate_count,
            null_counts=null_counts,
            column_stats=column_stats,
            elapsed_seconds=elapsed,
        )

    def _count_uniques(self, df: pl.DataFrame, column: str) -> int:
        if column not in df.columns:
            return 0
        return df.select(pl.col(column).n_unique()).item()

    def _count_nulls(self, df: pl.DataFrame) -> Dict[str, int]:
        return {col: df.select(pl.col(col).null_count()).item() for col in df.columns}

    def _count_duplicates(self, df: pl.DataFrame) -> int:
        if "store" in df.columns and "upc" in df.columns:
            subset = ["store", "upc"]
        else:
            return 0
        return df.select(pl.struct(subset).is_duplicated().sum()).item()

    def _compute_numeric_stats(self, df: pl.DataFrame) -> Dict[str, Dict[str, Any]]:
        numeric_cols = [
            col
            for col, dtype in df.schema.items()
            if dtype in (pl.Float64, pl.Float32, pl.Int64, pl.Int32, pl.Int16, pl.Int8)
        ]

        if not numeric_cols:
            return {}

        stats: Dict[str, Dict[str, Any]] = {}
        for col in numeric_cols:
            result = df.select(
                [
                    pl.col(col).min().alias("min"),
                    pl.col(col).max().alias("max"),
                    pl.col(col).mean().alias("mean"),
                    pl.col(col).median().alias("median"),
                ]
            ).to_dicts()[0]
            stats[col] = result

        return stats
