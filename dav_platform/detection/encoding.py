"""Encoding detection for files."""

from typing import Tuple

from dav_platform.core.contracts import EncodingType


def detect_encoding(raw_bytes: bytes) -> Tuple[EncodingType, float]:
    """Detect file encoding from raw bytes.

    Returns:
        Tuple of (EncodingType, confidence)
    """
    if not raw_bytes:
        return EncodingType.UTF_8, 0.0

    # Check for BOM (Byte Order Mark)
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return EncodingType.UTF_8, 1.0
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return EncodingType.UTF_16, 1.0

    # Try UTF-8 first
    try:
        raw_bytes.decode('utf-8')
        # Check for high-confidence UTF-8 indicators
        non_ascii = sum(1 for b in raw_bytes if b > 127)
        if non_ascii == 0:
            return EncodingType.UTF_8, 1.0
        # Has non-ASCII but decoded successfully
        return EncodingType.UTF_8, 0.9
    except UnicodeDecodeError:
        pass

    # Try Latin-1 (always succeeds as it maps all 256 bytes)
    try:
        decoded = raw_bytes.decode('latin-1')
        # Check if it looks like Latin-1 specific chars
        latin_chars = sum(1 for c in decoded if ord(c) in range(128, 256))
        if latin_chars > 0:
            return EncodingType.LATIN_1, 0.8
        return EncodingType.LATIN_1, 0.5
    except Exception:
        pass

    # Fallback
    return EncodingType.UNKNOWN, 0.0


def detect_encoding_from_lines(lines: list) -> Tuple[EncodingType, float]:
    """Detect encoding from text lines.

    Convenience wrapper for when text is already decoded.
    """
    if not lines:
        return EncodingType.UTF_8, 0.0

    # Join lines and encode to bytes for detection
    text = "".join(lines)
    raw_bytes = text.encode('utf-8', errors='replace')
    return detect_encoding(raw_bytes)
