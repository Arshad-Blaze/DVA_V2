"""Core contracts defining layer boundaries.

Every layer owns ONE contract.
Every layer consumes ONLY the contract produced by the previous layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, BinaryIO

import polars as pl


# ============================================================================
# Data Access Layer Contract
# ============================================================================

class DataSourceError(Exception):
    """Base exception for data source operations."""


@dataclass
class DataSourceEntry:
    """Represents a file or directory entry from a data source."""
    name: str
    path: str
    is_dir: bool = False
    size: Optional[int] = None
    modified: Optional[str] = None


@dataclass
class DirectorySummary:
    """Summary statistics for a directory.

    Used by Adaptive Data Access Strategy to decide
    stream vs batch copy vs chunk copy.
    """
    total_files: int = 0
    total_size: int = 0
    largest_file: Optional[str] = None
    largest_file_size: int = 0
    smallest_file: Optional[str] = None
    smallest_file_size: int = 0
    average_file_size: float = 0.0
    file_extensions: Dict[str, int] = field(default_factory=dict)
    estimated_transfer_bytes: int = 0


class IDataSource(ABC):
    """Contract for all data source connectors.

    Responsibilities:
    - Connect / Disconnect
    - Browse directories
    - Read files (sample, stream, download)
    - Return file metadata

    Nothing else.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Release connection and resources."""
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        ...

    @property
    def supports_direct_path(self) -> bool:
        """Whether files can be accessed via local paths.

        Local filesystems return True; remote sources return False.
        """
        return False

    @abstractmethod
    def list_directory(self, path: str) -> List[DataSourceEntry]:
        """List contents of a directory."""
        ...

    @abstractmethod
    def list_files(self, path: str) -> List[str]:
        """List files in a path (recursive for directories)."""
        ...

    @abstractmethod
    def read_sample(self, path: str, n: int = 100) -> str:
        """Read first n lines from a file."""
        ...

    @abstractmethod
    def open_stream(self, path: str) -> BinaryIO:
        """Open a binary stream for streaming reads."""
        ...

    @abstractmethod
    def download_if_required(self, path: str) -> str:
        """Download file to local if needed, return local path."""
        ...

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        ...

    @abstractmethod
    def stat(self, path: str) -> dict:
        """Get file/directory metadata."""
        ...

    @abstractmethod
    def get_file_size(self, path: str) -> int:
        """Get file size in bytes. Returns 0 for directories or errors."""
        ...

    @abstractmethod
    def directory_summary(self, path: str) -> "DirectorySummary":
        """Get summary statistics for a directory.

        Used by Adaptive Data Access Strategy to decide
        stream vs batch copy vs chunk copy.
        """
        ...

    @abstractmethod
    def get_server_info(self) -> dict:
        """Get connection metadata."""
        ...

    @abstractmethod
    def get_connection_string(self) -> str:
        """Get human-readable connection string."""
        ...


# ============================================================================
# Detection Layer Contract
# ============================================================================

class FileType(Enum):
    DELIMITED = "delimited"
    FIXED_WIDTH = "fixed_width"
    MULTILINE_DELIMITED = "multiline_delimited"
    FIXED_WIDTH_MULTILINE = "fixed_width_multiline"
    MIXED_RECORD = "mixed_record"
    EXCEL = "excel"
    UNKNOWN = "unknown"
    FIXED = "fixed_width"  # Alias


class EncodingType(Enum):
    UTF_8 = "utf-8"
    UTF_16 = "utf-16"
    LATIN_1 = "latin-1"
    ANSI = "ansi"
    UNKNOWN = "unknown"


@dataclass
class RecordTypeInfo:
    """Info about a detected record type."""
    prefix: str
    frequency: int = 0
    avg_record_length: float = 0.0
    sample_line: str = ""
    confidence: float = 0.0


@dataclass
class LayoutField:
    """A single field in a fixed-width layout."""
    start: int = 0
    width: int = 0
    datatype: str = "string"
    probable_name: str = ""
    confidence: float = 0.0


@dataclass
class ExcelSheetInfo:
    """Info about an Excel sheet."""
    name: str = ""
    row_count: int = 0
    column_count: int = 0
    has_header: bool = False
    columns: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class DetectionStatistics:
    """Statistics collected during detection."""
    estimated_rows: int = 0
    record_count: int = 0
    avg_record_length: float = 0.0
    min_record_length: int = 0
    max_record_length: int = 0
    avg_line_width: float = 0.0
    character_distribution: Dict[str, int] = field(default_factory=dict)
    delimiter_statistics: Dict[str, Any] = field(default_factory=dict)
    record_statistics: Dict[str, Any] = field(default_factory=dict)
    header_confidence: float = 0.0
    schema_confidence: float = 0.0
    encoding_confidence: float = 0.0


@dataclass
class CandidateMapping:
    """A candidate column mapping with confidence."""
    physical_column: str
    confidence: float = 0.0


@dataclass
class QuantityRecommendation:
    """Quantity intelligence recommendation."""
    recommended_column: Optional[str] = None
    recommendation_type: str = ""  # "weighted_qty", "units", "none"
    reason: str = ""
    confidence: float = 0.0


@dataclass
class DiscoveryResult:
    """Output of the Detection layer.

    This is the ONLY source of truth for file structure.
    No downstream layer may re-detect.
    """
    file_path: str
    file_type: FileType

    # Delimiter
    delimiter: Optional[str] = None
    delimiter_confidence: float = 0.0

    # Encoding
    encoding: str = "utf-8"
    encoding_type: EncodingType = EncodingType.UTF_8
    encoding_confidence: float = 0.0

    # Header
    has_header: bool = False
    header_confidence: float = 0.0
    header_start_line: int = 0
    data_start_line: int = 0
    trailer_start_line: Optional[int] = None

    # Multiline
    is_multiline: bool = False
    header_prefix: Optional[str] = None
    trailer_prefix: Optional[str] = None
    record_types: List[RecordTypeInfo] = field(default_factory=list)

    # Columns
    columns: List[str] = field(default_factory=list)

    # Record Hierarchy
    record_hierarchy: Optional[Dict[str, Any]] = None

    # Layout (fixed-width)
    layout_fields: List[LayoutField] = field(default_factory=list)
    layout_confidence: float = 0.0

    # Excel
    excel_sheets: List[ExcelSheetInfo] = field(default_factory=list)
    candidate_sheet: Optional[str] = None

    # Candidate Columns (19 roles)
    candidate_store: List[CandidateMapping] = field(default_factory=list)
    candidate_upc: List[CandidateMapping] = field(default_factory=list)
    candidate_description: List[CandidateMapping] = field(default_factory=list)
    candidate_brand: List[CandidateMapping] = field(default_factory=list)
    candidate_department: List[CandidateMapping] = field(default_factory=list)
    candidate_category: List[CandidateMapping] = field(default_factory=list)
    candidate_units: List[CandidateMapping] = field(default_factory=list)
    candidate_weighted_qty: List[CandidateMapping] = field(default_factory=list)
    candidate_price: List[CandidateMapping] = field(default_factory=list)
    candidate_sales: List[CandidateMapping] = field(default_factory=list)
    candidate_currency: List[CandidateMapping] = field(default_factory=list)
    candidate_date: List[CandidateMapping] = field(default_factory=list)
    candidate_time: List[CandidateMapping] = field(default_factory=list)
    candidate_promotion: List[CandidateMapping] = field(default_factory=list)
    candidate_store_type: List[CandidateMapping] = field(default_factory=list)
    candidate_region: List[CandidateMapping] = field(default_factory=list)
    candidate_division: List[CandidateMapping] = field(default_factory=list)
    candidate_uom: List[CandidateMapping] = field(default_factory=list)
    candidate_record_type: List[CandidateMapping] = field(default_factory=list)

    # Quantity Intelligence
    quantity_recommendation: Optional[QuantityRecommendation] = None

    # Statistics
    statistics: Optional[DetectionStatistics] = None

    # Overall
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Previews
    raw_preview: Optional[pl.DataFrame] = None
    flatten_preview: Optional[pl.DataFrame] = None
    canonical_preview: Optional[pl.DataFrame] = None


# ============================================================================
# Canonical Layer Contract
# ============================================================================

# Standard canonical column names
CANONICAL_COLUMNS = {
    "store": "Store identifier",
    "upc": "Universal Product Code",
    "description": "Product description",
    "quantity": "Resolved quantity (weighted or units)",
    "weight": "Weight value",
    "price": "Unit price",
    "category": "Product category",
    "brand": "Product brand",
    "department": "Department identifier",
    "date": "Transaction date",
    "uom": "Unit of measure",
}


@dataclass
class ColumnMapping:
    """A single physical-to-canonical column mapping."""
    physical_column: str
    canonical_name: str
    confidence: float = 0.0
    source: str = "candidate"  # "candidate", "rule", "user", "default"


@dataclass
class CanonicalMetadata:
    """Metadata about the canonical transformation."""
    total_rows: int = 0
    mapped_columns: int = 0
    unmapped_columns: int = 0
    quantity_column: Optional[str] = None
    quantity_type: str = "none"  # "weighted_qty", "units", "weight", "unit", "none"
    confidence: float = 0.0
    source_file_type: str = ""
    encoding: str = "utf-8"
    flatten_strategy: str = "none"  # "hierarchy", "multiline", "direct"
    uom_strategy: str = "none"  # "detected", "default"
    validation_summary: Optional[dict] = None
    ignored_columns: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    transformation_log: List[str] = field(default_factory=list)


@dataclass
class CanonicalDataset:
    """Standardized dataset with business-meaningful column names.

    No downstream layer should know retailer-specific column names.
    """
    file_path: str = ""
    physical_to_canonical: Dict[str, str] = field(default_factory=dict)
    canonical_columns: List[str] = field(default_factory=list)
    column_mappings: List[ColumnMapping] = field(default_factory=list)
    dataframe: Optional[pl.DataFrame] = None
    metadata: Optional[CanonicalMetadata] = None
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    @property
    def df(self) -> Optional[pl.DataFrame]:
        return self.dataframe

    @property
    def row_count(self) -> int:
        return self.dataframe.height if self.dataframe is not None else 0

    @property
    def column_count(self) -> int:
        return self.dataframe.width if self.dataframe is not None else 0

    @property
    def resolved_quantity_column(self) -> Optional[str]:
        return self.metadata.quantity_column if self.metadata else None


# ============================================================================
# Requirement Layer Contract
# ============================================================================

class ProcessingMode(Enum):
    AGGREGATE_ONLY = "aggregate_only"
    AGGREGATE_AND_CALCULATE = "aggregate_and_calculate"
    RAW_REVIEW = "raw_review"


class BusinessGoal(Enum):
    """Business objectives the user may want to accomplish."""
    RAW_REVIEW = "raw_review"
    VALIDATION = "validation"
    FORMAT_CHANGE = "format_change"
    MIGRATION = "migration"
    COMPARISON = "comparison"
    REPORTING = "reporting"
    AGGREGATION = "aggregation"
    CALCULATION = "calculation"


@dataclass
class CapabilityMatrix:
    """Determines what operations the dataset supports."""
    can_aggregate: bool = False
    can_calculate: bool = False
    can_compare: bool = False
    can_validate: bool = False
    can_migrate: bool = False
    can_report: bool = False
    can_review: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {
            "can_aggregate": self.can_aggregate,
            "can_calculate": self.can_calculate,
            "can_compare": self.can_compare,
            "can_validate": self.can_validate,
            "can_migrate": self.can_migrate,
            "can_report": self.can_report,
            "can_review": self.can_review,
        }


@dataclass
class ExecutionStep:
    """A single step in an execution plan."""
    step_number: int
    action: str
    description: str
    required: bool = True
    layer: str = ""  # which layer executes this step


@dataclass
class OperationContext:
    """Context passed through operation and processing layers."""
    mode: ProcessingMode = ProcessingMode.AGGREGATE_ONLY
    options: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Sprint 4B fields
    business_goal: Optional[BusinessGoal] = None
    capability_matrix: Optional[CapabilityMatrix] = None
    execution_plan: List[ExecutionStep] = field(default_factory=list)
    recommended_workflow: str = ""
    required_inputs: List[str] = field(default_factory=list)
    missing_inputs: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: float = 0.0


# ============================================================================
# Operation Layer Contract
# ============================================================================

class ExecutionState(Enum):
    """State of an execution step or overall execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionStepResult:
    """Result of executing a single step."""
    step_number: int = 0
    action: str = ""
    state: ExecutionState = ExecutionState.PENDING
    result: Any = None
    error: Optional[str] = None
    elapsed_seconds: float = 0.0
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationLog:
    """Structured execution log entry."""
    timestamp: str = ""
    level: str = "info"  # info, warning, error
    step_number: Optional[int] = None
    action: str = ""
    message: str = ""
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetadata:
    """Metadata about the execution."""
    workflow: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0
    execution_duration: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    outcome: str = ""  # success, partial, failed, cancelled


@dataclass
class ExecutionResult:
    """Result of executing an OperationContext."""
    state: ExecutionState = ExecutionState.PENDING
    step_results: List[ExecutionStepResult] = field(default_factory=list)
    metadata: Optional[ExecutionMetadata] = None
    logs: List[OperationLog] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.state == ExecutionState.COMPLETED

    @property
    def failed(self) -> bool:
        return self.state == ExecutionState.FAILED

    @property
    def cancelled(self) -> bool:
        return self.state == ExecutionState.CANCELLED


@dataclass
class ProcessingResult:
    """Output of the Processing layer."""
    df: pl.DataFrame
    operation: str = ""
    row_count: int = 0
    column_count: int = 0
    elapsed_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @classmethod
    def from_df(cls, df: pl.DataFrame, operation: str = "",
                elapsed_seconds: float = 0.0,
                metadata: Optional[Dict[str, Any]] = None,
                errors: Optional[List[str]] = None) -> "ProcessingResult":
        return cls(
            df=df,
            operation=operation,
            row_count=df.height,
            column_count=df.width,
            elapsed_seconds=elapsed_seconds,
            metadata=metadata or {},
            errors=errors or [],
        )

    @classmethod
    def error(cls, operation: str, message: str) -> "ProcessingResult":
        return cls(
            df=pl.DataFrame(),
            operation=operation,
            errors=[message],
        )


# ============================================================================
# Validation Layer Contract
# ============================================================================

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Single validation issue."""
    rule: str
    message: str
    severity: ValidationSeverity
    row_count: int = 0
    column: Optional[str] = None


@dataclass
class ValidationResult:
    """Output of the Validation layer."""
    passed: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    total_rows_checked: int = 0
    error_count: int = 0
    warning_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Reporting Layer Contract
# ============================================================================

class ReportFormat(Enum):
    EXCEL = "excel"
    CSV = "csv"
    PARQUET = "parquet"


@dataclass
class ReportOutput:
    """Output of the Reporting layer."""
    file_path: str
    format: ReportFormat
    sheet_name: Optional[str] = None
    row_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
