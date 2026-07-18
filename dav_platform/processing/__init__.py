"""Processing Layer — Computation engine for DVA Platform V2.

Responsibilities:
- Execute business computations requested by Operation Layer
- Aggregate data by canonical columns
- Calculate metrics on canonical fields
- Generate processing statistics
- Support chunk-based streaming processing

Input: CanonicalDataset + OperationContext/ProcessingConfig
Output: ProcessingResult, AggregationResult, CalculationResult, ProcessingStatistics

This layer performs NO business validation, NO workflow selection,
NO report generation, NO retailer-specific logic.
"""

from dav_platform.processing.engine import ProcessingEngine
from dav_platform.processing.aggregator import Aggregator
from dav_platform.processing.calculator import Calculator
from dav_platform.processing.statistics import StatisticsEngine
from dav_platform.processing.streaming import StreamingProcessor
from dav_platform.processing.configuration import build_config

__all__ = [
    "ProcessingEngine",
    "Aggregator",
    "Calculator",
    "StatisticsEngine",
    "StreamingProcessor",
    "build_config",
]
