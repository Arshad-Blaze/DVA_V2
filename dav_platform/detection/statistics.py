"""Statistics collection during detection."""

from collections import Counter
from typing import Dict, List, Optional

from dav_platform.core.contracts import DetectionStatistics


def collect_statistics(
    lines: List[str],
    delimiter: Optional[str] = None,
) -> DetectionStatistics:
    """Collect comprehensive statistics from sample lines."""
    if not lines:
        return DetectionStatistics()

    stats = DetectionStatistics()
    non_empty = [l for l in lines if l.strip()]

    # Basic counts
    stats.record_count = len(non_empty)
    stats.estimated_rows = len(non_empty)  # Sample-based estimate

    # Line lengths
    lengths = [len(line) for line in non_empty]
    stats.min_record_length = min(lengths) if lengths else 0
    stats.max_record_length = max(lengths) if lengths else 0
    stats.avg_record_length = sum(lengths) / max(len(lengths), 1)
    stats.avg_line_width = stats.avg_record_length

    # Character distribution
    char_counter: Counter = Counter()
    for line in non_empty:
        for ch in line:
            char_counter[ch] += 1
    stats.character_distribution = dict(char_counter.most_common(50))

    # Delimiter statistics
    if delimiter:
        stats.delimiter_statistics = _compute_delimiter_stats(non_empty, delimiter)

    # Record statistics (line length distribution)
    length_counter = Counter(lengths)
    stats.record_statistics = {
        "length_distribution": dict(length_counter.most_common(20)),
        "unique_lengths": len(length_counter),
    }

    return stats


def _compute_delimiter_stats(lines: List[str], delimiter: str) -> Dict:
    """Compute delimiter-specific statistics."""
    counts = []
    for line in lines:
        count = 0
        in_quotes = False
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == delimiter and not in_quotes:
                count += 1
        counts.append(count)

    if not counts:
        return {}

    avg = sum(counts) / len(counts)
    variance = sum((c - avg) ** 2 for c in counts) / len(counts)

    return {
        "delimiter": delimiter,
        "avg_field_count": round(avg + 1, 1),  # +1 because delimiters separate fields
        "min_field_count": min(counts) + 1,
        "max_field_count": max(counts) + 1,
        "variance": round(variance, 2),
        "consistency": round(max(0.0, 1.0 - variance / (avg + 1)), 2),
    }
