"""Streaming canonical dataset.

Supports chunk-based pipelines for large files.
Avoids materializing the full dataset unless required.

This module does NOT parse files directly.
It receives pre-parsed chunks and applies canonical transformations.
"""

from typing import Dict, Generator, Optional

import polars as pl

from dav_platform.core.contracts import CanonicalDataset


def transform_chunks(
    chunks: Generator[pl.DataFrame, None, None],
    result,
    chunk_size: int = 1000,
) -> Generator[CanonicalDataset, None, None]:
    """Transform pre-parsed data chunks through canonical pipeline.

    Receives already-parsed chunks and applies canonical transformations
    (mapping, quantity, UOM normalization).

    Args:
        chunks: Generator of pre-parsed DataFrames
        result: DiscoveryResult from Detection
        chunk_size: Rows per chunk (unused, kept for API compatibility)

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
    total_rows: int = 0,
    avg_row_bytes: int = 200,
) -> Dict[str, int]:
    """Estimate memory usage for the canonical dataset.

    Args:
        total_rows: Estimated total rows (0 if unknown)
        avg_row_bytes: Average row size in bytes

    Returns:
        Dict with estimated_bytes, estimated_rows, avg_row_bytes, chunk_recommendation
    """
    if total_rows <= 0:
        total_rows = 10000
        # Only set default avg_row_bytes if it wasn't explicitly provided
        if avg_row_bytes == 200:
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
