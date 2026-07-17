"""Header detection for delimited files."""

from typing import List, Optional


def detect_header(lines: List[str], delimiter: str) -> bool:
    """Detect if the first line is a header row.

    Heuristic: If most values in the first line contain alphabetic characters,
    it's likely a header.
    """
    if not lines or not delimiter:
        return False

    first_line = lines[0].strip()
    if not first_line:
        return False

    values = first_line.split(delimiter)
    if not values:
        return False

    alpha_count = sum(
        1 for v in values
        if any(c.isalpha() for c in v.strip())
    )

    # Header if more than half the values contain alphabetic characters
    return alpha_count >= len(values) / 2


def detect_header_prefix(lines: List[str]) -> Optional[str]:
    """Detect multi-character HDR prefix in fixed-width multiline files.

    Returns the longest prefix found, or None.
    """
    if not lines:
        return None

    prefixes = set()
    for line in lines:
        if not line:
            continue
        # Look for 2+ alpha chars followed by digit — common HDR pattern
        for i in range(2, min(6, len(line))):
            if line[:i].isalpha() and i < len(line) and line[i].isdigit():
                prefixes.add(line[:i])
                break

    if not prefixes:
        return None

    # Return longest prefix
    return sorted(prefixes, key=len, reverse=True)[0]
