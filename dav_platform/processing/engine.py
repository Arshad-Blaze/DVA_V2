"""Processing Engine — top-level orchestrator."""
import time
from typing import Optional, List
import polars as pl
from dav_platform.core.contracts import (
    CanonicalDataset, ProcessingConfig, ProcessingResult,
    AggregationResult, CalculationResult, ProcessingStatistics,
    OperationContext,
)
from dav_platform.processing.aggregator import Aggregator
from dav_platform.processing.calculator import Calculator
from dav_platform.processing.statistics import StatisticsEngine
from dav_platform.processing.streaming import StreamingProcessor
from dav_platform.processing.configuration import build_config


class ProcessingEngine:
    """Top-level processing engine. Orchestrates aggregation, calculation, and statistics.

    This layer performs computations ONLY. It does NOT:
    - decide workflows
    - make business decisions
    - validate business correctness
    - generate reports
    - know retailer formats
    - know physical schemas
    """

    def __init__(self):
        self._aggregator = Aggregator()
        self._calculator = Calculator()
        self._statistics = StatisticsEngine()
        self._streaming = StreamingProcessor()

    def process(
        self,
        dataset: CanonicalDataset,
        config: Optional[ProcessingConfig] = None,
        context: Optional[OperationContext] = None,
    ) -> ProcessingResult:
        """Execute the full processing pipeline.

        - Build config if not provided
        - Run aggregation if group_columns and aggregations are configured
        - Run calculations if configured
        - Run statistics if configured
        - Return ProcessingResult with final DataFrame and metadata
        - Never modifies input dataset
        """
        start = time.time()

        if dataset.dataframe is None or dataset.dataframe.is_empty():
            return ProcessingResult.error("process", "Dataset has no dataframe")

        if config is None:
            config = build_config(dataset=dataset, context=context)

        errors: List[str] = []
        metadata: dict = {
            "steps": [],
            "original_rows": dataset.row_count,
            "original_columns": dataset.column_count,
        }

        current_df = dataset.dataframe.clone()

        # Step 1: Aggregation
        if config.group_columns and config.aggregation_configs:
            try:
                # Build a temporary dataset with current_df
                agg_dataset = CanonicalDataset(
                    dataframe=current_df,
                    canonical_columns=dataset.canonical_columns,
                )
                agg_result = self._aggregator.aggregate(
                    agg_dataset,
                    config.group_columns,
                    config.aggregation_configs,
                )
                current_df = agg_result.data
                metadata["steps"].append({
                    "operation": "aggregation",
                    "rows": agg_result.row_count,
                    "elapsed": agg_result.elapsed_seconds,
                })
            except Exception as e:
                errors.append(f"Aggregation failed: {e}")

        # Step 2: Calculations
        if config.calculation_configs:
            try:
                calc_dataset = CanonicalDataset(
                    dataframe=current_df,
                    canonical_columns=dataset.canonical_columns,
                )
                calc_result = self._calculator.calculate(
                    calc_dataset,
                    config.calculation_configs,
                )
                current_df = calc_result.data
                errors.extend(calc_result.errors)
                metadata["steps"].append({
                    "operation": "calculation",
                    "rows": calc_result.row_count,
                    "elapsed": calc_result.elapsed_seconds,
                })
            except Exception as e:
                errors.append(f"Calculation failed: {e}")

        # Step 3: Statistics
        if config.compute_statistics:
            try:
                stats_dataset = CanonicalDataset(
                    dataframe=current_df,
                    canonical_columns=dataset.canonical_columns,
                )
                stats = self._statistics.compute(stats_dataset)
                metadata["statistics"] = {
                    "total_rows": stats.total_rows,
                    "duplicate_count": stats.duplicate_count,
                    "null_counts": stats.null_counts,
                }
                metadata["steps"].append({
                    "operation": "statistics",
                    "elapsed": stats.elapsed_seconds,
                })
            except Exception as e:
                errors.append(f"Statistics failed: {e}")

        elapsed = time.time() - start
        metadata["total_elapsed"] = elapsed

        return ProcessingResult.from_df(
            current_df,
            operation="process",
            elapsed_seconds=elapsed,
            metadata=metadata,
            errors=errors,
        )

    def aggregate(
        self, dataset: CanonicalDataset, config: ProcessingConfig
    ) -> AggregationResult:
        """Run aggregation only."""
        return self._aggregator.aggregate(
            dataset,
            config.group_columns,
            config.aggregation_configs,
        )

    def calculate(
        self, dataset: CanonicalDataset, config: ProcessingConfig
    ) -> CalculationResult:
        """Run calculations only."""
        return self._calculator.calculate(
            dataset,
            config.calculation_configs,
        )

    def compute_statistics(
        self, dataset: CanonicalDataset
    ) -> ProcessingStatistics:
        """Compute statistics only."""
        return self._statistics.compute(dataset)
