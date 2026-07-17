"""Unit tests for DetectionEngine."""

import pytest

from dav_platform.connection.local import LocalDataSource
from dav_platform.detection.engine import DetectionEngine
from dav_platform.core.contracts import FileType


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
        assert result.record_types == ["D", "H", "T"]
        assert result.trailer_prefix == "T"

    def test_detect_fixed_width(self, detection_engine, fixed_width_file):
        result = detection_engine.detect(fixed_width_file)
        assert result.file_type == FileType.FIXED

    def test_confidence_score(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        assert 0.0 <= result.confidence <= 1.0

    def test_warnings_generated(self, detection_engine, fixed_width_file):
        result = detection_engine.detect(fixed_width_file)
        assert len(result.warnings) > 0

    def test_candidate_columns(self, detection_engine, csv_file):
        result = detection_engine.detect(csv_file)
        # CSV has name, price, quantity - should detect candidates
        assert len(result.candidate_price_columns) > 0 or len(result.candidate_quantity_columns) > 0
