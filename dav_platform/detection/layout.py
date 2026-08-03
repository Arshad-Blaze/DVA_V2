"""Layout intelligence for fixed-width files.

Analyzes character positions to suggest column boundaries.
"""

from typing import List

from dav_platform.core.contracts import LayoutField


def detect_column_breaks(lines: List[str], min_gap: int = 2) -> List[int]:
    """Detect column break positions by finding consistent gaps.

    Analyzes character positions across lines to find positions where
    whitespace consistently appears (column boundaries).
    """
    if not lines or min_gap < 1:
        return []

    # Find the max line length
    max_len = max(len(line) for line in lines) if lines else 0
    if max_len == 0:
        return []

    # Count whitespace at each position
    whitespace_counts = []
    for pos in range(max_len):
        count = 0
        for line in lines:
            if pos >= len(line):
                count += 1  # Beyond line end counts as whitespace
            elif line[pos] == ' ':
                count += 1
        whitespace_counts.append(count)

    # Find positions where most lines have whitespace (potential breaks)
    threshold = len(lines) * 0.7  # 70% of lines
    breaks = []
    in_gap = False
    gap_start = 0

    for pos in range(max_len):
        if whitespace_counts[pos] >= threshold:
            if not in_gap:
                gap_start = pos
                in_gap = True
        else:
            if in_gap:
                gap_len = pos - gap_start
                if gap_len >= min_gap:
                    # Use the center of the gap as the break point
                    break_pos = gap_start + gap_len // 2
                    breaks.append(break_pos)
                in_gap = False

    # Handle trailing gap
    if in_gap:
        gap_len = max_len - gap_start
        if gap_len >= min_gap:
            breaks.append(gap_start + gap_len // 2)

    return breaks


def generate_layout_fields(
    lines: List[str],
    breaks: List[int],
    has_header: bool = False,
) -> List[LayoutField]:
    """Generate layout field suggestions from detected breaks.

    Returns a list of LayoutField with start, width, probable_name, confidence.
    """
    if not breaks:
        return []

    # Add implicit boundaries
    boundaries = [0] + breaks + [max(len(line) for line in lines) if lines else 0]

    fields = []
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        width = end - start

        if width <= 0:
            continue

        # Analyze column content
        col_values = []
        for line in lines:
            if start < len(line):
                col_values.append(line[start:min(end, len(line))].strip())

        # Determine datatype
        datatype = _infer_datatype(col_values)

        # Generate probable name
        probable_name = _generate_column_name(i, datatype, col_values)

        # Calculate confidence based on data consistency
        confidence = _calculate_field_confidence(col_values, width)

        fields.append(LayoutField(
            start=start,
            width=width,
            datatype=datatype,
            probable_name=probable_name,
            confidence=confidence,
        ))

    return fields


def _infer_datatype(values: List[str]) -> str:
    """Infer the datatype of a column from its values."""
    if not values:
        return "string"

    # Check for numeric
    numeric_count = 0
    decimal_count = 0
    for v in values:
        if not v:
            continue
        try:
            float(v)
            numeric_count += 1
            if '.' in v:
                decimal_count += 1
        except ValueError:
            pass

    total = len([v for v in values if v])
    if total == 0:
        return "string"

    if numeric_count == total:
        if decimal_count > 0:
            return "decimal"
        return "integer"

    # Check for date patterns
    date_count = sum(1 for v in values if _looks_like_date(v))
    if date_count > total * 0.5:
        return "date"

    return "string"


def _looks_like_date(value: str) -> bool:
    """Check if a value looks like a date."""
    if not value:
        return False
    # Simple date patterns
    date_seps = ['-', '/', '.']
    for sep in date_seps:
        if sep in value:
            parts = value.split(sep)
            if len(parts) == 3:
                try:
                    all(int(p) for p in parts)
                    return True
                except ValueError:
                    pass
    return False


def _generate_column_name(index: int, datatype: str, values: List[str]) -> str:
    """Generate a probable column name based on position and content."""
    # Check if values look like specific data
    if datatype == "date":
        return "date"
    if datatype in ("integer", "decimal"):
        # Check for patterns
        if values and any(len(v) >= 12 for v in values if v):
            return "id"
        return f"numeric_{index + 1}"
    return f"column_{index + 1}"


def _calculate_field_confidence(values: List[str], width: int) -> float:
    """Calculate confidence for a layout field."""
    if not values or width <= 0:
        return 0.0

    # Factors: data consistency, fill rate, width reasonableness
    non_empty = sum(1 for v in values if v)
    fill_rate = non_empty / max(len(values), 1)

    # Check if values consistently use the width
    width_usage = sum(1 for v in values if len(v) > width * 0.5) / max(len(values), 1)

    # Reasonable width (1-50 chars)
    width_score = 1.0 if 1 <= width <= 50 else 0.5

    confidence = (fill_rate * 0.4 + width_usage * 0.3 + width_score * 0.3)
    return round(min(1.0, confidence), 2)
