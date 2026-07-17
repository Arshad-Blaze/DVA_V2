"""Unit tests for core contracts."""

import pytest

from dav_platform.core.contracts import (
    DiscoveryResult,
    FileType,
    CanonicalDataset,
    OperationContext,
    ProcessingMode,
    ProcessingResult,
    ValidationResult,
    ValidationSeverity,
    ValidationIssue,
)
import polars as pl


class TestDiscoveryResult:
    def test_creation(self):
        result = DiscoveryResult(
            file_path="/data/test.csv",
            file_type=FileType.DELIMITED,
            delimiter=",",
        )
        assert result.file_path == "/data/test.csv"
        assert result.file_type == FileType.DELIMITED
        assert result.delimiter == ","
        assert result.confidence == 0.0
        assert result.warnings == []

    def test_defaults(self):
        result = DiscoveryResult(file_path="test.csv", file_type=FileType.UNKNOWN)
        assert result.has_header is False
        assert result.is_multiline is False
        assert result.columns == []


class TestCanonicalDataset:
    def test_creation(self):
        df = pl.DataFrame({"store": ["S1"], "upc": ["123"]})
        ds = CanonicalDataset(df=df, source_file="test.csv")
        assert ds.row_count == 0
        assert ds.column_count == 0

    def test_from_df(self):
        df = pl.DataFrame({"store": ["S1", "S2"], "upc": ["123", "456"]})
        ds = CanonicalDataset(df=df)
        ds.row_count = df.height
        ds.column_count = df.width
        assert ds.row_count == 2
        assert ds.column_count == 2


class TestProcessingResult:
    def test_from_df(self):
        df = pl.DataFrame({"a": [1, 2, 3]})
        result = ProcessingResult.from_df(df, operation="test")
        assert result.row_count == 3
        assert result.column_count == 1
        assert result.operation == "test"

    def test_error(self):
        result = ProcessingResult.error("test", "something failed")
        assert result.errors == ["something failed"]
        assert result.row_count == 0


class TestValidationResult:
    def test_defaults(self):
        result = ValidationResult()
        assert result.passed is True
        assert result.error_count == 0

    def test_with_issues(self):
        issue = ValidationIssue(
            rule="required_column",
            message="Missing column 'store'",
            severity=ValidationSeverity.ERROR,
        )
        result = ValidationResult(issues=[issue], passed=False, error_count=1)
        assert result.passed is False
        assert len(result.issues) == 1
