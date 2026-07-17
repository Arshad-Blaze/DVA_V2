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
    MULTILINE = "multiline"
    FIXED_WIDTH_MULTILINE = "fixed_width_multiline"
    EXCEL = "excel"
    UNKNOWN = "unknown"


@dataclass
class DiscoveryResult:
    """Output of the Detection layer.

    This is the ONLY source of truth for file structure.
    No downstream layer may re-detect.
    """
    file_path: str
    file_type: FileType
    delimiter: Optional[str] = None
    encoding: str = "utf-8"
    has_header: bool = False
    is_multiline: bool = False
    header_prefix: Optional[str] = None
    trailer_prefix: Optional[str] = None
    record_types: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    candidate_quantity_columns: List[str] = field(default_factory=list)
    candidate_price_columns: List[str] = field(default_factory=list)
    candidate_uom_columns: List[str] = field(default_factory=list)
    record_hierarchy: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    raw_preview: Optional[pl.DataFrame] = None
    flatten_preview: Optional[pl.DataFrame] = None
    canonical_preview: Optional[pl.DataFrame] = None


# ============================================================================
# Canonical Layer Contract
# ============================================================================

@dataclass
class CanonicalDataset:
    """Standardized dataset with business-meaningful column names.

    No downstream layer should know retailer-specific column names.
    """
    df: pl.DataFrame
    source_file: str = ""
    row_count: int = 0
    column_count: int = 0
    resolved_quantity_column: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Requirement Layer Contract
# ============================================================================

class ProcessingMode(Enum):
    AGGREGATE_ONLY = "aggregate_only"
    AGGREGATE_AND_CALCULATE = "aggregate_and_calculate"
    RAW_REVIEW = "raw_review"


@dataclass
class OperationContext:
    """Context passed through operation and processing layers."""
    mode: ProcessingMode = ProcessingMode.AGGREGATE_ONLY
    options: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Operation Layer Contract
# ============================================================================

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
