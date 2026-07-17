"""Unit tests for confidence score calculation."""

import pytest

from dav_platform.detection.confidence import compute_confidence_score


class TestComputeConfidenceScore:
    def test_perfect_delimited(self):
        result = {
            "file_type": "delimited",
            "delimiter": ",",
            "_delimiter_scores": {",": 10, "|": 0, "\t": 0, ";": 0},
            "is_multiline": False,
            "has_header": True,
            "trailer_prefix": None,
        }
        assert compute_confidence_score(result) == 1.0

    def test_fixed_width_low_confidence(self):
        result = {
            "file_type": "fixed",
            "delimiter": None,
            "is_multiline": False,
            "has_header": False,
        }
        score = compute_confidence_score(result)
        assert score < 1.0

    def test_ambiguous_delimiter(self):
        result = {
            "file_type": "delimited",
            "delimiter": ",",
            "_delimiter_scores": {",": 5, "|": 4, "\t": 0, ";": 0},
            "is_multiline": False,
            "has_header": True,
        }
        score = compute_confidence_score(result)
        assert score < 1.0

    def test_no_header_penalty(self):
        result = {
            "file_type": "delimited",
            "delimiter": ",",
            "_delimiter_scores": {",": 10, "|": 0, "\t": 0, ";": 0},
            "is_multiline": False,
            "has_header": False,
        }
        score = compute_confidence_score(result)
        assert score < 1.0

    def test_unknown_file_type(self):
        result = {"file_type": None}
        assert compute_confidence_score(result) == 0.0

    def test_multiline_no_prefix_penalty(self):
        result = {
            "file_type": "delimited",
            "delimiter": "|",
            "_delimiter_scores": {"|": 10},
            "is_multiline": True,
            "header_prefix": None,
            "ml_record_types": None,
            "has_header": False,
            "trailer_prefix": None,
        }
        score = compute_confidence_score(result)
        assert score < 0.8
