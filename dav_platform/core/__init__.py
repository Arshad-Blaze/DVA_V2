"""Core contracts and shared types for DVA Platform v2."""

from dav_platform.core.contracts import (
    # Connection Layer
    IDataSource,
    DataSourceEntry,
    DataSourceError,
    DirectorySummary,
    # Detection Layer
    DiscoveryResult,
    FileType,
    EncodingType,
    RecordTypeInfo,
    LayoutField,
    ExcelSheetInfo,
    DetectionStatistics,
    CandidateMapping,
    QuantityRecommendation,
    # Canonical Layer
    CanonicalDataset,
    CanonicalMetadata,
    ColumnMapping,
    CANONICAL_COLUMNS,
    # Requirement Layer
    OperationContext,
    ProcessingMode,
    BusinessGoal,
    CapabilityMatrix,
    ExecutionStep,
    # Operation Layer
    ExecutionState,
    ExecutionStepResult,
    OperationLog,
    ExecutionMetadata,
    ExecutionResult,
    # Shared / cross-layer
    ProcessingResult,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
    ReportFormat,
    ReportOutput,
)

__all__ = [
    # Connection Layer
    "IDataSource",
    "DataSourceEntry",
    "DataSourceError",
    "DirectorySummary",
    # Detection Layer
    "DiscoveryResult",
    "FileType",
    "EncodingType",
    "RecordTypeInfo",
    "LayoutField",
    "ExcelSheetInfo",
    "DetectionStatistics",
    "CandidateMapping",
    "QuantityRecommendation",
    # Canonical Layer
    "CanonicalDataset",
    "CanonicalMetadata",
    "ColumnMapping",
    "CANONICAL_COLUMNS",
    # Requirement Layer
    "OperationContext",
    "ProcessingMode",
    "BusinessGoal",
    "CapabilityMatrix",
    "ExecutionStep",
    # Operation Layer
    "ExecutionState",
    "ExecutionStepResult",
    "OperationLog",
    "ExecutionMetadata",
    "ExecutionResult",
    # Shared / cross-layer
    "ProcessingResult",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ReportFormat",
    "ReportOutput",
]
