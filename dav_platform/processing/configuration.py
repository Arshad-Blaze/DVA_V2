"""Processing configuration builder."""
from typing import List, Optional
from dav_platform.core.contracts import (
    ProcessingConfig, AggregationConfig, CalculationConfig,
    AggregationStrategy, CanonicalDataset, OperationContext,
)

GROUPABLE_COLUMNS = {"store", "upc", "category", "brand", "department"}


def build_config(
    dataset: Optional[CanonicalDataset] = None,
    context: Optional[OperationContext] = None,
    group_columns: Optional[List[str]] = None,
    aggregations: Optional[List[AggregationConfig]] = None,
    calculations: Optional[List[CalculationConfig]] = None,
    chunk_size: Optional[int] = None,
    streaming: Optional[bool] = None,
) -> ProcessingConfig:
    """Build a ProcessingConfig from inputs.

    Priority: explicit args > context hints > dataset defaults.
    If no group_columns provided and dataset has groupable columns, use them.
    """
    # Resolve group columns: explicit > context > dataset defaults
    resolved_groups = group_columns
    if resolved_groups is None and context is not None:
        ctx_groups = context.options.get("group_columns")
        if isinstance(ctx_groups, list):
            resolved_groups = ctx_groups
    if resolved_groups is None and dataset is not None:
        resolved_groups = _detect_group_columns(dataset)

    # Resolve aggregations: explicit > context > dataset defaults
    resolved_aggs = aggregations
    if resolved_aggs is None and context is not None:
        ctx_aggs = context.options.get("aggregation_configs")
        if isinstance(ctx_aggs, list):
            resolved_aggs = ctx_aggs
    if resolved_aggs is None:
        resolved_aggs = _default_aggregations(resolved_groups)

    # Resolve calculations: explicit > context > dataset defaults
    resolved_calcs = calculations
    if resolved_calcs is None and context is not None:
        ctx_calcs = context.options.get("calculation_configs")
        if isinstance(ctx_calcs, list):
            resolved_calcs = ctx_calcs
    if resolved_calcs is None and dataset is not None:
        resolved_calcs = _detect_calculations(dataset)

    # Resolve chunk_size: explicit > context > default
    resolved_chunk = chunk_size
    if resolved_chunk is None and context is not None:
        ctx_chunk = context.options.get("chunk_size")
        if isinstance(ctx_chunk, int) and ctx_chunk > 0:
            resolved_chunk = ctx_chunk
    if resolved_chunk is None:
        resolved_chunk = 10_000

    resolved_streaming = streaming
    if resolved_streaming is None and context is not None:
        ctx_stream = context.options.get("streaming")
        if isinstance(ctx_stream, bool):
            resolved_streaming = ctx_stream
    if resolved_streaming is None:
        resolved_streaming = True

    return ProcessingConfig(
        group_columns=resolved_groups or [],
        aggregation_configs=resolved_aggs or [],
        calculation_configs=resolved_calcs or [],
        chunk_size=resolved_chunk,
        streaming=resolved_streaming,
    )


def _detect_group_columns(dataset: CanonicalDataset) -> List[str]:
    """Detect groupable columns from canonical_columns."""
    if not dataset.canonical_columns:
        return []
    return [col for col in dataset.canonical_columns if col in GROUPABLE_COLUMNS]


def _detect_calculations(dataset: CanonicalDataset) -> List[CalculationConfig]:
    """Suggest default calculations based on available columns."""
    if dataset.dataframe is None or not dataset.canonical_columns:
        return []

    available = set(dataset.dataframe.columns)
    calcs: List[CalculationConfig] = []

    # If quantity exists, compute total as a placeholder
    if "quantity" in available and "price" in available:
        calcs.append(CalculationConfig(
            name="total_value",
            columns=["quantity", "price"],
            operation="ratio",
            alias="total_value",
        ))

    return calcs


def _default_aggregations(group_columns: Optional[List[str]]) -> List[AggregationConfig]:
    """Generate default aggregation configs when groups are present."""
    if not group_columns:
        return []

    aggs: List[AggregationConfig] = []

    if "quantity" not in group_columns:
        aggs.append(AggregationConfig(
            column="quantity",
            strategy=AggregationStrategy.SUM,
            alias="total_quantity",
        ))

    if "price" not in group_columns:
        aggs.append(AggregationConfig(
            column="price",
            strategy=AggregationStrategy.MEAN,
            alias="avg_price",
        ))

    return aggs
