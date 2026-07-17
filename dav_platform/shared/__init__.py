"""Shared utilities for DVA Platform v2."""

from dav_platform.shared.report import generate_discovery_report, DiscoveryReport
from dav_platform.shared.quantity import recommend_quantity_column

__all__ = [
    "generate_discovery_report",
    "DiscoveryReport",
    "recommend_quantity_column",
]
