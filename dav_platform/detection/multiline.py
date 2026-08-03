"""Multiline and record type detection.

Supports dynamic record type discovery with statistics.
"""

from typing import Dict, List, Optional, Set

from dav_platform.core.contracts import RecordTypeInfo


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
    """Detect if file uses multiline records."""
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

    if (len(alpha_prefixes) >= 2 and
        alpha_count >= len(lines) * 0.4 and
        not _first_line_is_header(lines)):
        return True

    # Check backslash continuations
    backslash = sum(line.rstrip().endswith("\\") for line in lines)
    if backslash >= 5:
        return True

    # Check fixed-width multiline
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

    repeated = sum(1 for cnt in prefix_line_count.values() if cnt >= 2)
    if repeated >= 1 and not has_delimiter_data:
        return True

    return False


def detect_record_types(lines: List[str], delimiter: Optional[str] = None) -> List[str]:
    """Detect record type prefixes from sample lines (simple list)."""
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


def detect_record_types_detailed(
    lines: List[str],
    delimiter: Optional[str] = None,
) -> List[RecordTypeInfo]:
    """Detect record types with statistics.

    Returns detailed RecordTypeInfo for each discovered record type.
    """
    if not lines:
        return []

    # Count prefixes and collect samples
    prefix_data: Dict[str, List[str]] = {}
    for line in lines:
        if not line:
            continue
        first = line[0]
        if first.isalpha() and len(line) >= 2:
            sep = line[1]
            if sep in ",|\t;" if delimiter is None else sep == delimiter:
                if first not in prefix_data:
                    prefix_data[first] = []
                prefix_data[first].append(line)

    result = []
    total_lines = len(lines)

    for prefix, type_lines in prefix_data.items():
        freq = len(type_lines)
        avg_len = sum(len(l) for l in type_lines) / max(freq, 1)
        sample = type_lines[0] if type_lines else ""

        # Confidence based on frequency and consistency
        freq_ratio = freq / max(total_lines, 1)
        length_variance = sum((len(l) - avg_len) ** 2 for l in type_lines) / max(freq, 1)
        consistency = max(0.0, 1.0 - (length_variance / (avg_len + 1)))

        confidence = round(min(1.0, freq_ratio * 0.6 + consistency * 0.4), 2)

        result.append(RecordTypeInfo(
            prefix=prefix,
            frequency=freq,
            avg_record_length=round(avg_len, 1),
            sample_line=sample,
            confidence=confidence,
        ))

    # Sort by frequency descending
    result.sort(key=lambda r: r.frequency, reverse=True)
    return result


def detect_trailer_prefix(lines: List[str]) -> Optional[str]:
    """Auto-detect trailer prefix in multiline files."""
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


def build_record_hierarchy(
    record_types: List[RecordTypeInfo],
    lines: List[str],
) -> Optional[Dict]:
    """Build record hierarchy from detected record types.

    Returns a generic hierarchy structure:
    {
        "header": {"prefix": "H", "frequency": 1},
        "detail": [{"prefix": "D", "frequency": N}],
        "trailer": {"prefix": "T", "frequency": 1}
    }
    """
    if not record_types:
        return None

    hierarchy: Dict = {
        "header": None,
        "detail": [],
        "trailer": None,
        "other": [],
    }

    # Sort by frequency: lowest freq = header/trailer, highest = detail
    sorted_types = sorted(record_types, key=lambda r: r.frequency)

    for rt in sorted_types:
        if rt.frequency == 1 and hierarchy["header"] is None:
            hierarchy["header"] = {"prefix": rt.prefix, "frequency": rt.frequency}
        elif rt.frequency == 1 and hierarchy["trailer"] is None:
            hierarchy["trailer"] = {"prefix": rt.prefix, "frequency": rt.frequency}
        elif rt.frequency > 1:
            hierarchy["detail"].append({"prefix": rt.prefix, "frequency": rt.frequency})
        else:
            hierarchy["other"].append({"prefix": rt.prefix, "frequency": rt.frequency})

    return hierarchy if hierarchy["header"] or hierarchy["detail"] else None
