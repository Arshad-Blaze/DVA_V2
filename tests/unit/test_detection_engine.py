"""Unit tests for DetectionEngine."""

import pytest

from dav_platform.connection.local import LocalDataSource
from dav_platform.detection.engine import DetectionEngine
from dav_platform.core.contracts import FileType, RecordTypeInfo


@pytest.fixture
def local_source():
    return LocalDataSource()


@pytest.fixture
def detection_engine(local_source):
    return DetectionEngine(local_source)


@pytest.fixture
def csv_file(tmp_path):
    content = "name,price,quantity\nApple,1.50,100\nBanana,0.75,200\n"
    file_path = tmp_path / "test.csv"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def pipe_file(tmp_path):
    content = "name|price|quantity\nApple|1.50|100\nBanana|0.75|200\n"
    file_path = tmp_path / "test.txt"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def multiline_file(tmp_path):
    content = "H|STORE001|2024-01-01\nD|ITEM001|100\nD|ITEM002|200\nT|2\nT|count\n"
    file_path = tmp_path / "multiline.txt"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def fixed_width_file(tmp_path):
    content = "name     price    quantity\nApple    1.50     100\nBanana   0.75     200\n"
    file_path = tmp_path / "fixed.txt"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def store_item_file(tmp_path):
    content = "H|STORE001|2024-01-01\nS|ITEM001|100|1.50\nS|ITEM002|200|0.75\nD|ITEM003|50|2.00\nD|ITEM004|75|1.25\nT|4\n"
    file_path = tmp_path / "store_item.txt"
    file_path.write_text(content)
    return str(file_path)


class TestDetectionEngine:
    def test_detect_csv(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert result.file_type == FileType.DELIMITED
        assert result.delimiter == ","
        assert result.has_header is True
        assert "name" in result.columns

    def test_detect_pipe(self, detection_engine, pipe_file):
        result = detection_engine.detect(pipe_file)
        assert result.file_type == FileType.DELIMITED
        assert result.delimiter == "|"
        assert result.has_header is True

    def test_detect_multiline(self, detection_engine, multiline_file):
        result = detection_engine.detect(multiline_file)
        assert result.is_multiline is True
        assert len(result.record_types) > 0
        assert result.trailer_prefix == "T"

    def test_detect_fixed_width(self, detection_engine, fixed_width_file):
        result = detection_engine.detect(fixed_width_file)
        assert result.file_type == FileType.FIXED_WIDTH

    def test_confidence_score(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert 0.0 <= result.confidence <= 1.0

    def test_warnings_generated(self, detection_engine, fixed_width_file):
        result = detection_engine.detect(fixed_width_file)
        assert len(result.warnings) > 0

    def test_encoding_detected(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert result.encoding is not None
        assert result.encoding_confidence > 0.0

    def test_statistics_collected(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert result.statistics is not None
        assert result.statistics.record_count > 0

    def test_raw_preview_generated(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert result.raw_preview is not None
        assert result.raw_preview.height > 0

    def test_store_item_file(self, detection_engine, store_item_file):
        result = detection_engine.detect(store_item_file)
        assert result.is_multiline is True
        assert len(result.record_types) >= 2
