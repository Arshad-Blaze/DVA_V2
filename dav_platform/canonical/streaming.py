"""Streaming canonical dataset.

Supports chunk-based pipelines for large files.
Avoids materializing the full dataset unless required.

NOTE: This module does NOT parse files directly.
It receives pre-parsed data chunks and applies canonical transformations.
"""

from typing import Generator, List, Optional

import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    DiscoveryResult,
)


def transform_chunks(
    chunks: Generator[pl.DataFrame, None, None],
    result: DiscoveryResult,
    chunk_size: int = 1000,
) -> Generator[CanonicalDataset, None, None]:
    """Transform pre-parsed data chunks through canonical pipeline.

    This is the correct streaming interface:
    - Receives already-parsed chunks (from Detection or data access layer)
    - Applies canonical transformations (mapping, quantity, UOM)
    - Yields CanonicalDataset objects (maintains contract boundary)

    Args:
        chunks: Generator of pre-parsed DataFrames
        result: DiscoveryResult from Detection
        chunk_size: Rows per chunk (for metadata)

    Yields:
        CanonicalDataset objects for each chunk
    """
    from dav_platform.canonical.engine import CanonicalEngine

    engine = CanonicalEngine()

    for chunk in chunks:
        if chunk is None or chunk.is_empty():
            continue

        dataset = engine.transform(result, data=chunk)
        yield dataset


def estimate_memory_usage(
    result: DiscoveryResult,
    total_rows: int = 0,
    avg_row_bytes: int = 200,
) -> dict:
    """Estimate memory usage for the canonical dataset.

    Args:
        result: DiscoveryResult for context
        total_rows: Estimated total rows (0 if unknown)
        avg_row_bytes: Average row size in bytes

    Returns:
        Dict with estimated_bytes, estimated_rows, chunk_recommendation
    """
    if total_rows <= 0:
        # Default estimate
        total_rows = 10000
        avg_row_bytes = 200

    estimated_bytes = total_rows * avg_row_bytes

    # Recommend chunk size based on row size
    if avg_row_bytes < 100:
        chunk_size = 10000
    elif avg_row_bytes < 500:
        chunk_size = 5000
    else:
        chunk_size = 1000

    return {
        "estimated_bytes": estimated_bytes,
        "estimated_rows": total_rows,
        "avg_row_bytes": avg_row_bytes,
        "chunk_recommendation": chunk_size,
    }
