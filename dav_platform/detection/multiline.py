"""Multiline and record type detection."""

from typing import List, Optional, Set


TRAILER_PREFIX_CANDIDATES = ["TRL", "TR", "T", "TL", "TRAILER", "F"]


def _first_line_is_header(lines: List[str]) -> bool:
    """Check if the first line looks like a column header."""
    if not lines:
        return False

    for delim in (",", "|", "\t", ";"):
        if delim in lines[0]:
            parts = lines[0].split(delim)
            long_names = sum(
                1 for p in parts
                if len(p.strip()) >= 3 and any(c.isalpha() for c in p.strip())
            )
            if long_names >= len(parts) * 0.4:
                return True
            return False
    return False


def detect_multiline(lines: List[str]) -> bool:
    """Detect if file uses multiline records.

    Checks for:
    - Delimited multiline (H|, D| prefixes)
    - Fixed-width multiline (alphanumeric prefixes)
    - Backslash continuations
    """
    if not lines:
        return False

    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return False

    # Check delimited multiline: 2+ single-letter prefixes (H|, D|, etc.)
    alpha_prefixes: Set[str] = set()
    alpha_count = 0
    for line in lines:
        if len(line) >= 2 and line[0].isalpha() and line[1] in ",|\t;":
            alpha_prefixes.add(line[0])
            alpha_count += 1

    # Require at least 2 distinct prefixes AND at least 40% of lines match
    # AND the first line doesn't look like a header
    if (len(alpha_prefixes) >= 2 and
        alpha_count >= len(lines) * 0.4 and
        not _first_line_is_header(lines)):
        return True

    # Check backslash continuations
    backslash = sum(line.rstrip().endswith("\\") for line in lines)
    if backslash >= 5:
        return True

    # Check fixed-width multiline: lines start with alphabetic prefix (2+ letters)
    # followed by digits — plain data lines don't.
    prefix_line_count: dict = {}
    data_count = 0
    has_delimiter_data = False
    for line in lines:
        found = False
        for i in range(2, min(6, len(line))):
            if line[:i].isalpha() and i < len(line) and line[i].isdigit():
                prefix_line_count[line[:i]] = prefix_line_count.get(line[:i], 0) + 1
                found = True
                break
        if not found and line and line[0].isdigit():
            data_count += 1
            if any(d in line for d in ",|\t;"):
                has_delimiter_data = True

    # Require prefix to repeat on 2+ lines AND no delimiter in data lines
    repeated = sum(1 for cnt in prefix_line_count.values() if cnt >= 2)
    if repeated >= 1 and not has_delimiter_data:
        return True

    return False


def detect_record_types(lines: List[str], delimiter: Optional[str] = None) -> List[str]:
    """Detect record type prefixes from sample lines."""
    if not lines:
        return []

    prefixes: Set[str] = set()
    for line in lines:
        if not line:
            continue
        first = line[0]
        if first.isalpha() and len(line) >= 2:
            sep = line[1]
            if sep in ",|\t;" if delimiter is None else sep == delimiter:
                prefixes.add(first)

    return sorted(prefixes)


def detect_trailer_prefix(lines: List[str]) -> Optional[str]:
    """Auto-detect trailer prefix in multiline files.

    Checks common trailer prefix candidates against the last portion of
    the sample — trailer records typically appear near the end.
    Returns the first confirmed prefix or None.
    """
    if not lines:
        return None

    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return None

    for candidate in TRAILER_PREFIX_CANDIDATES:
        if _has_trailer_candidate(lines, candidate):
            return candidate

    return None


def _has_trailer_candidate(lines: List[str], prefix: str) -> bool:
    """Check if at least 2 lines start with prefix followed by digit/delimiter."""
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix):
            rest = stripped[len(prefix):]
            if rest and (rest[0].isdigit() or rest[0] in ",|\t;"):
                count += 1
    return count >= 2
