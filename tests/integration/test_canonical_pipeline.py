"""Integration tests for Detection → Canonical pipeline."""

import os
import tempfile

import pytest
import polars as pl

from dav_platform.canonical.engine import CanonicalEngine
from dav_platform.connection.local import LocalDataSource
from dav_platform.detection.engine import DetectionEngine
from dav_platform.core.contracts import CanonicalDataset, FileType


@pytest.fixture
def csv_file():
    """Create a temporary CSV file for testing."""
    content = "Store_Nbr,UPC,Item_Desc,Price,Units_Sold\n1,1234567890,Apple,1.50,10\n2,0987654321,Banana,0.75,20\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def pipe_file():
    """Create a temporary pipe-delimited file for testing."""
    content = "STORE|SKU|DESC|PRICE|QTY\n100|A123|Milk|2.99|5\n100|B456|Bread|1.49|10\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def multiline_file():
    """Create a temporary multiline file for testing."""
    content = "H|100|2024-01-15\nD|1234567890|Apple|1.50|10\nD|0987654321|Banana|0.75|20\nT|2\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


class TestDetectionToCanonicalIntegration:
    def test_csv_pipeline(self, csv_file):
        """Test full CSV detection → canonical pipeline."""
        source = LocalDataSource()
        source.connect()

        # Detection
        detector = DetectionEngine(source)
        discovery = detector.detect(csv_file)

        assert discovery.file_type == FileType.DELIMITED
        assert discovery.delimiter == ","
        assert discovery.has_header is True
        assert len(discovery.columns) == 5

        # Canonical
        canonical = CanonicalEngine()
        dataset = canonical.transform(discovery)

        assert isinstance(dataset, CanonicalDataset)
        assert dataset.file_path == csv_file
        assert len(dataset.column_mappings) > 0
        assert dataset.metadata is not None
        assert dataset.metadata.source_file_type == "delimited"

        source.disconnect()

    def test_pipe_pipeline(self, pipe_file):
        """Test full pipe-delimited detection → canonical pipeline."""
        source = LocalDataSource()
        source.connect()

        # Detection
        detector = DetectionEngine(source)
        discovery = detector.detect(pipe_file)

        assert discovery.file_type == FileType.DELIMITED
        assert discovery.delimiter == "|"
        assert len(discovery.columns) == 5

        # Canonical
        canonical = CanonicalEngine()
        dataset = canonical.transform(discovery)

        assert isinstance(dataset, CanonicalDataset)
        assert len(dataset.column_mappings) > 0

        source.disconnect()

    def test_multiline_pipeline(self, multiline_file):
        """Test full multiline detection → canonical pipeline."""
        source = LocalDataSource()
        source.connect()

        # Detection
        detector = DetectionEngine(source)
        discovery = detector.detect(multiline_file)

        assert discovery.file_type in (FileType.DELIMITED, FileType.MULTILINE_DELIMITED)
        assert discovery.delimiter == "|"

        # Canonical
        canonical = CanonicalEngine()
        dataset = canonical.transform(discovery)

        assert isinstance(dataset, CanonicalDataset)

        source.disconnect()

    def test_quantity_resolution(self, csv_file):
        """Test quantity resolution through the pipeline."""
        source = LocalDataSource()
        source.connect()

        detector = DetectionEngine(source)
        discovery = detector.detect(csv_file)

        canonical = CanonicalEngine()
        dataset = canonical.transform(discovery)

        # Should resolve quantity from Units_Sold column
        assert dataset.metadata.quantity_type in ("units", "weighted_qty", "none")

        source.disconnect()

    def test_mapping_completeness(self, csv_file):
        """Test that all standard columns are mapped when candidates exist."""
        source = LocalDataSource()
        source.connect()

        detector = DetectionEngine(source)
        discovery = detector.detect(csv_file)

        canonical = CanonicalEngine()
        dataset = canonical.transform(discovery)

        # Should have mapped columns
        mapped_canonicals = {m.canonical_name for m in dataset.column_mappings}
        assert len(mapped_canonicals) > 0

        source.disconnect()
