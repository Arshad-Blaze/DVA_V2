"""Delimiter detection for delimited files."""

from typing import List, Optional, Tuple


CANDIDATE_DELIMITERS = [",", "|", "\t", ";"]


def count_delimiters_outside_quotes(line: str, delimiter: str) -> int:
    """Count delimiter occurrences outside quoted fields."""
    count = 0
    in_quotes = False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == delimiter and not in_quotes:
            count += 1
    return count


def detect_delimiter(lines: List[str]) -> Tuple[Optional[str], dict]:
    """Detect the most likely delimiter from sample lines.

    Returns:
        Tuple of (best_delimiter, scores_dict)
    """
    if not lines:
        return None, {}

    scores = {}
    for delim in CANDIDATE_DELIMITERS:
        scores[delim] = sum(count_delimiters_outside_quotes(line, delim) for line in lines)

    if not any(scores.values()):
        return None, scores

    best = max(scores, key=scores.get)
    return best, scores


def validate_delimiter_consistency(lines: List[str], delimiter: str) -> float:
    """Validate delimiter consistency across lines.

    Returns consistency score 0.0-1.0.
    """
    if not lines or not delimiter:
        return 0.0

    counts = [count_delimiters_outside_quotes(line, delimiter) for line in lines]
    if not counts:
        return 0.0

    # If no delimiters found at all, return 0
    if all(c == 0 for c in counts):
        return 0.0

    # Perfect consistency if all counts are equal
    if len(set(counts)) == 1:
        return 1.0

    # Partial consistency based on variance
    avg = sum(counts) / len(counts)
    if avg == 0:
        return 0.0

    variance = sum((c - avg) ** 2 for c in counts) / len(counts)
    # Lower variance = higher consistency
    consistency = max(0.0, 1.0 - (variance / (avg + 1)))
    return round(consistency, 2)
