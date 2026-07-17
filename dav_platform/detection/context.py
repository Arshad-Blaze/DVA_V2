"""DiscoveryContext — internal analysis structure.

This is INTERNAL ONLY. Never returned to downstream layers.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DiscoveryContext:
    """Internal analysis context for detection.

    Contains all intermediate analysis data.
    This is INTERNAL ONLY — never returned to downstream layers.
    """
    raw_sample: str = ""
    lines: List[str] = field(default_factory=list)
    non_empty_lines: List[str] = field(default_factory=list)

    # Layout statistics
    avg_line_length: float = 0.0
    min_line_length: int = 0
    max_line_length: int = 0

    # Record statistics
    total_lines: int = 0
    blank_lines: int = 0
    data_lines: int = 0
