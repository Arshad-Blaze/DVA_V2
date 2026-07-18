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
    # Processing Layer
    AggregationStrategy,
    AggregationConfig,
    AggregationResult,
    CalculationConfig,
    CalculationResult,
    ProcessingStatistics,
    ProcessingConfig,
    # Validation Layer
    ValidationSeverity,
    ValidationIssue,
    ValidationResult,
    ValidationRule,
    ValidationConfig,
    ValidationSummary,
    ValidationStatistics,
    ValidationReportData,
    # Output Layer
    OutputFormat,
    ExportManifest,
    OutputStatistics,
    OutputArtifacts,
    OutputConfig,
    # Shared / cross-layer
    ProcessingResult,
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
    # Processing Layer
    "AggregationStrategy",
    "AggregationConfig",
    "AggregationResult",
    "CalculationConfig",
    "CalculationResult",
    "ProcessingStatistics",
    "ProcessingConfig",
    # Validation Layer
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    "ValidationRule",
    "ValidationConfig",
    "ValidationSummary",
    "ValidationStatistics",
    "ValidationReportData",
    # Output Layer
    "OutputFormat",
    "ExportManifest",
    "OutputStatistics",
    "OutputArtifacts",
    "OutputConfig",
    # Shared / cross-layer
    "ProcessingResult",
]
