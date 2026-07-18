"""Core contracts and shared types for DVA Platform v2."""

from dav_platform.core.contracts import (
    IDataSource,
    DataSourceEntry,
    DataSourceError,
    DiscoveryResult,
    CanonicalDataset,
    OperationContext,
    ProcessingMode,
    BusinessGoal,
    CapabilityMatrix,
    ExecutionStep,
    ProcessingResult,
    ValidationResult,
    ReportOutput,
)

__all__ = [
    "IDataSource",
    "DataSourceEntry",
    "DataSourceError",
    "DiscoveryResult",
    "CanonicalDataset",
    "OperationContext",
    "ProcessingMode",
    "BusinessGoal",
    "CapabilityMatrix",
    "ExecutionStep",
    "ProcessingResult",
    "ValidationResult",
    "ReportOutput",
]
