"""Unit tests for discovery report generation."""

import pytest

from dav_platform.shared.report import generate_discovery_report, DiscoveryReport
from dav_platform.core.contracts import (
    DiscoveryResult,
    FileType,
    CandidateMapping,
    RecordTypeInfo,
)


class TestGenerateDiscoveryReport:
    def test_basic_report(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            delimiter=",",
            has_header=True,
            confidence=0.95,
        )
        report = generate_discovery_report(result)
        assert isinstance(report, DiscoveryReport)
        assert report.file_path == "/test.csv"
        assert report.file_type == "delimited"
        assert report.delimiter == ","
        assert report.confidence == 0.95

    def test_report_with_candidates(self):
        result = DiscoveryResult(
            file_path="/test.csv",
            file_type=FileType.DELIMITED,
            candidate_store=[CandidateMapping(physical_column="Store", confidence=0.9)],
            candidate_price=[CandidateMapping(physical_column="Price", confidence=0.8)],
        )
        report = generate_discovery_report(result)
        assert "store" in report.candidate_columns
        assert "Store" in report.candidate_columns["store"]

    def test_report_with_record_types(self):
        result = DiscoveryResult(
            file_path="/test.txt",
            file_type=FileType.DELIMITED,
            record_types=[
                RecordTypeInfo(prefix="H", frequency=1),
                RecordTypeInfo(prefix="D", frequency=5),
            ],
        )
        report = generate_discovery_report(result)
        assert report.file_path == "/test.txt"
