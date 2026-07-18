import pytest
import polars as pl

from dav_platform.core.contracts import (
    CanonicalDataset,
    CanonicalMetadata,
    ProcessingConfig,
    ProcessingResult,
)
from dav_platform.processing.streaming import StreamingProcessor


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


@pytest.mark.unit
class TestStreamingProcessor:
    def test_chunk_dataframe_yields_correct_chunks(self):
        df = pl.DataFrame({"x": list(range(10))})
        proc = StreamingProcessor()
        chunks = list(proc.chunk_dataframe(df, chunk_size=3))
        assert len(chunks) == 4
        assert chunks[0].height == 3
        assert chunks[1].height == 3
        assert chunks[2].height == 3
        assert chunks[3].height == 1

    def test_chunk_dataframe_exact_multiple(self):
        df = pl.DataFrame({"x": list(range(6))})
        proc = StreamingProcessor()
        chunks = list(proc.chunk_dataframe(df, chunk_size=3))
        assert len(chunks) == 2
        assert all(c.height == 3 for c in chunks)

    def test_chunk_dataframe_single_row_chunks(self):
        df = pl.DataFrame({"x": [1, 2, 3]})
        proc = StreamingProcessor()
        chunks = list(proc.chunk_dataframe(df, chunk_size=1))
        assert len(chunks) == 3

    def test_chunk_dataframe_zero_size_raises(self):
        df = pl.DataFrame({"x": [1]})
        proc = StreamingProcessor()
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            list(proc.chunk_dataframe(df, chunk_size=0))

    def test_process_chunks_identity_processor(self):
        dataset = _make_dataset()
        config = ProcessingConfig(chunk_size=2)
        proc = StreamingProcessor()

        result = proc.process_chunks(dataset, config, processor=lambda df: df)

        assert isinstance(result, ProcessingResult)
        assert result.row_count == 5
        assert result.errors == []

    def test_process_chunks_transformation_processor(self):
        dataset = _make_dataset()
        config = ProcessingConfig(chunk_size=2)
        proc = StreamingProcessor()

        def add_double(df: pl.DataFrame) -> pl.DataFrame:
            return df.with_columns((pl.col("units") * 2).alias("units_doubled"))

        result = proc.process_chunks(dataset, config, processor=add_double)

        assert "units_doubled" in result.df.columns
        assert result.row_count == 5
        assert result.df["units_doubled"][0] == 20

    def test_process_chunks_empty_dataset(self):
        df = pl.DataFrame({"store": [], "upc": [], "units": [], "price": []})
        dataset = CanonicalDataset(
            file_path="/empty.csv",
            canonical_columns=["store", "upc", "units", "price"],
            dataframe=df,
        )
        config = ProcessingConfig(chunk_size=2)
        proc = StreamingProcessor()

        result = proc.process_chunks(dataset, config, processor=lambda df: df)

        assert len(result.errors) > 0

    def test_estimate_chunks(self):
        proc = StreamingProcessor()
        assert proc.estimate_chunks(row_count=10, chunk_size=3) == 4
        assert proc.estimate_chunks(row_count=9, chunk_size=3) == 3
        assert proc.estimate_chunks(row_count=1, chunk_size=10) == 1
        assert proc.estimate_chunks(row_count=0, chunk_size=5) == 0
        assert proc.estimate_chunks(row_count=10, chunk_size=0) == 0
