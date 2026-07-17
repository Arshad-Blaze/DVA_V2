"""Unit tests for encoding detection."""

import pytest

from dav_platform.detection.encoding import detect_encoding, detect_encoding_from_lines
from dav_platform.core.contracts import EncodingType


class TestDetectEncoding:
    def test_utf8_ascii(self):
        data = b"hello world\n"
        enc, conf = detect_encoding(data)
        assert enc == EncodingType.UTF_8
        assert conf == 1.0

    def test_utf8_bom(self):
        data = b'\xef\xbb\xbfhello'
        enc, conf = detect_encoding(data)
        assert enc == EncodingType.UTF_8
        assert conf == 1.0

    def test_utf16_bom(self):
        data = b'\xff\xfehello'
        enc, conf = detect_encoding(data)
        assert enc == EncodingType.UTF_16
        assert conf == 1.0

    def test_latin1(self):
        data = "café résumé".encode('latin-1')
        enc, conf = detect_encoding(data)
        assert enc == EncodingType.LATIN_1
        assert conf > 0.5

    def test_empty_data(self):
        enc, conf = detect_encoding(b"")
        assert enc == EncodingType.UTF_8
        assert conf == 0.0


class TestDetectEncodingFromLines:
    def test_ascii_lines(self):
        lines = ["hello", "world"]
        enc, conf = detect_encoding_from_lines(lines)
        assert enc == EncodingType.UTF_8

    def test_empty_lines(self):
        enc, conf = detect_encoding_from_lines([])
        assert enc == EncodingType.UTF_8
        assert conf == 0.0
