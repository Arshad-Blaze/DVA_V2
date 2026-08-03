"""Streaming processing for large datasets."""
import time
from typing import Iterator, List, Callable
import polars as pl
from dav_platform.core.contracts import CanonicalDataset, ProcessingConfig, ProcessingResult


class StreamingProcessor:
    """Process large datasets in chunks to avoid full materialization."""

    def process_chunks(
        self,
        dataset: CanonicalDataset,
        config: ProcessingConfig,
        processor: Callable[[pl.DataFrame], pl.DataFrame],
    ) -> ProcessingResult:
        """Process dataset in chunks using the provided processor function.

        - Splits dataframe into chunks of config.chunk_size
        - Applies processor to each chunk
        - Concatenates results
        - Returns ProcessingResult
        """
        start = time.time()

        if dataset.dataframe is None or dataset.dataframe.is_empty():
            return ProcessingResult.error("streaming", "Dataset has no dataframe")

        df = dataset.dataframe
        chunk_size = config.chunk_size or 10_000
        chunk_count = 0
        processed_chunks: List[pl.DataFrame] = []
        errors: List[str] = []

        for chunk in self.chunk_dataframe(df, chunk_size):
            try:
                result = processor(chunk)
                processed_chunks.append(result)
                chunk_count += 1
            except Exception as e:
                errors.append(f"Chunk {chunk_count} failed: {e}")
                chunk_count += 1

        if not processed_chunks:
            return ProcessingResult.error(
                "streaming", "All chunks failed or dataset was empty"
            )

        combined = pl.concat(processed_chunks)
        elapsed = time.time() - start

        return ProcessingResult.from_df(
            combined,
            operation="streaming",
            elapsed_seconds=elapsed,
            metadata={
                "chunks_processed": chunk_count,
                "chunk_size": chunk_size,
                "original_rows": df.height,
                "result_rows": combined.height,
            },
            errors=errors,
        )

    def chunk_dataframe(self, df: pl.DataFrame, chunk_size: int) -> Iterator[pl.DataFrame]:
        """Yield chunks of a DataFrame."""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")

        total_rows = df.height
        offset = 0

        while offset < total_rows:
            end = min(offset + chunk_size, total_rows)
            yield df.slice(offset, end - offset)
            offset = end

    def estimate_chunks(self, row_count: int, chunk_size: int) -> int:
        """Estimate number of chunks for a given row count."""
        if chunk_size <= 0:
            return 0
        return (row_count + chunk_size - 1) // chunk_size
