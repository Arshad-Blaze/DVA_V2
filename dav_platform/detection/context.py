"""DiscoveryContext — internal analysis structure.

This is INTERNAL ONLY. Never returned to downstream layers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CharacterAnalysis:
    """Character-level analysis of sample data."""
    total_chars: int = 0
    printable_chars: int = 0
    whitespace_chars: int = 0
    digit_chars: int = 0
    alpha_chars: int = 0
    special_chars: int = 0
    char_frequency: Dict[str, int] = field(default_factory=dict)


@dataclass
class LineAnalysis:
    """Per-line analysis."""
    line_index: int = 0
    length: int = 0
    stripped_length: int = 0
    is_blank: bool = False
    delimiter_count: int = 0
    leading_alpha: bool = False
    leading_digit: bool = False
    prefix: Optional[str] = None


@dataclass
class PrefixMap:
    """Map of prefix patterns found in the data."""
    prefix: str = ""
    count: int = 0
    avg_length: float = 0.0
    sample_lines: List[str] = field(default_factory=list)


@dataclass
class FrequencyMap:
    """Frequency distribution of values in a position."""
    position: int = 0
    values: Dict[str, int] = field(default_factory=dict)


@dataclass
class DiscoveryContext:
    """Internal analysis context for detection.

    Contains all intermediate analysis data.
    This is INTERNAL ONLY — never returned to downstream layers.
    """
    raw_sample: str = ""
    lines: List[str] = field(default_factory=list)
    non_empty_lines: List[str] = field(default_factory=list)

    # Character analysis
    character_analysis: Optional[CharacterAnalysis] = None

    # Line analysis
    line_analyses: List[LineAnalysis] = field(default_factory=list)

    # Prefix analysis
    prefix_maps: List[PrefixMap] = field(default_factory=list)

    # Frequency maps (for delimiter, etc.)
    frequency_maps: List[FrequencyMap] = field(default_factory=list)

    # Layout statistics
    avg_line_length: float = 0.0
    min_line_length: int = 0
    max_line_length: int = 0

    # Record statistics
    total_lines: int = 0
    blank_lines: int = 0
    data_lines: int = 0
