"""Detection service — manages detection state, results, timeline, overrides.

Consumes the backend DiscoveryResult contract type for data.
UI NEVER detects files — only visualizes detection results.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import asdict

from dav_platform.core.contracts import (
    DiscoveryResult,
    FileType,
    EncodingType,
    RecordTypeInfo,
    LayoutField,
    DetectionStatistics,
)


DETECTION_STEPS = [
    "File Loaded",
    "Sample Read",
    "Encoding Detected",
    "Delimiter Detected",
    "Header Detected",
    "Layout Detected",
    "Detection Complete",
]


class DetectionService:
    """Manages detection state within the UI session.

    Stores detection results, timeline, warnings, and manual overrides.
    Never performs actual detection — only visualizes and collects overrides.
    """

    def __init__(self, context=None):
        self._context = context
        self._result: Optional[DiscoveryResult] = None
        self._timeline: List[Dict[str, Any]] = []
        self._warnings: List[Dict[str, Any]] = []
        self._overrides: Dict[str, Any] = {}
        self._detection_status: str = "idle"
        self._selected_file: Optional[str] = None
        self._selected_files: List[str] = []
        self._connection_id: Optional[str] = None
        self._accepted: bool = False
        self._on_change: Optional[Callable] = None

        # Seed a demo detection result
        self._seed_demo()

    def _seed_demo(self) -> None:
        self._selected_file = "sales_q2_2026.csv"
        self._selected_files = [
            "sales_q2_2026.csv",
            "inventory_june.dat",
            "customer_feedback.txt",
        ]
        self._connection_id = "production_data"
        self._result = self._build_demo_result()
        self._timeline = self._build_demo_timeline()
        self._warnings = self._build_demo_warnings()

    def _build_demo_result(self) -> DiscoveryResult:
        return DiscoveryResult(
            file_path="/data/production/sales_q2_2026.csv",
            file_type=FileType.DELIMITED,
            delimiter=",",
            delimiter_confidence=0.97,
            encoding="utf-8",
            encoding_type=EncodingType.UTF_8,
            encoding_confidence=1.0,
            has_header=True,
            header_confidence=0.98,
            header_start_line=0,
            data_start_line=1,
            is_multiline=False,
            columns=[
                "Store", "Date", "UPC", "Description", "Category",
                "Units", "Price", "Sales", "Promotion",
            ],
            confidence=0.95,
        )

    def _build_demo_timeline(self) -> List[Dict[str, Any]]:
        now = datetime.now()
        return [
            {"step": "File Loaded", "status": "completed", "detail": f"Loaded {self._selected_file}", "time": now},
            {"step": "Sample Read", "status": "completed", "detail": "200 lines sampled", "time": now},
            {"step": "Encoding Detected", "status": "completed", "detail": "UTF-8 (confidence: 1.0)", "time": now},
            {"step": "Delimiter Detected", "status": "completed", "detail": "Comma ',' (confidence: 0.97)", "time": now},
            {"step": "Header Detected", "status": "completed", "detail": "Row 1 (confidence: 0.98)", "time": now},
            {"step": "Layout Detected", "status": "completed", "detail": "9 columns (confidence: 0.95)", "time": now},
            {"step": "Detection Complete", "status": "completed", "detail": "All checks passed", "time": now},
        ]

    def _build_demo_warnings(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "info",
                "message": "File contains UTF-8 BOM — automatically handled",
                "detail": "The file starts with a UTF-8 BOM sequence which was stripped during processing.",
            },
            {
                "type": "warning",
                "message": "Low confidence on delimiter for lines 42-45",
                "detail": "Lines 42-45 have inconsistent field counts (8 instead of 9). "
                         "May contain embedded delimiters or malformed data.",
            },
            {
                "type": "suggestion",
                "message": "Consider verifying Promotion column",
                "detail": "The 'Promotion' column has 40% null values in the sample. "
                         "Verify this is expected before processing.",
            },
        ]

    # ------------------------------------------------------------------
    # Detection execution
    # ------------------------------------------------------------------

    def run_detection(self, file_path: Optional[str] = None) -> None:
        """Simulate running detection."""
        if file_path:
            self._selected_file = file_path
        self._detection_status = "running"
        self._result = self._build_demo_result()
        self._timeline = self._build_demo_timeline()
        self._warnings = self._build_demo_warnings()
        self._overrides.clear()
        self._accepted = False
        self._detection_status = "completed"
        self._notify()

    def validate_detection(self) -> bool:
        """Validate current detection."""
        if self._result is None:
            return False
        # In a real app, this would invoke the backend Validation layer
        return True

    def accept_detection(self) -> None:
        self._accepted = True
        self._detection_status = "accepted"
        self._notify()

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------

    @property
    def has_overrides(self) -> bool:
        return len(self._overrides) > 0

    def set_override(self, key: str, value: Any) -> None:
        self._overrides[key] = {"value": value, "timestamp": datetime.now()}
        self._accepted = False
        self._notify()

    def get_override(self, key: str) -> Optional[Any]:
        entry = self._overrides.get(key)
        return entry["value"] if entry else None

    def clear_override(self, key: str) -> None:
        self._overrides.pop(key, None)
        self._notify()

    def clear_all_overrides(self) -> None:
        self._overrides.clear()
        self._notify()

    def get_effective_value(self, key: str, detected_value: Any) -> Any:
        override = self.get_override(key)
        return override if override is not None else detected_value

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def result(self) -> Optional[DiscoveryResult]:
        return self._result

    @property
    def timeline(self) -> List[Dict[str, Any]]:
        return list(self._timeline)

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return list(self._warnings)

    @property
    def detection_status(self) -> str:
        return self._detection_status

    @detection_status.setter
    def detection_status(self, value: str) -> None:
        self._detection_status = value
        self._notify()

    @property
    def selected_file(self) -> Optional[str]:
        return self._selected_file

    @selected_file.setter
    def selected_file(self, value: str) -> None:
        self._selected_file = value

    @property
    def selected_files(self) -> List[str]:
        return list(self._selected_files)

    @property
    def is_accepted(self) -> bool:
        return self._accepted

    @property
    def connection_id(self) -> Optional[str]:
        return self._connection_id

    def switch_file(self, file_name: str) -> None:
        self._selected_file = file_name
        self.run_detection()

    def get_detection_summary(self) -> Dict[str, Any]:
        if not self._result:
            return {}
        return {
            "file_type": self._result.file_type.value if self._result.file_type else "unknown",
            "delimiter": self._result.delimiter,
            "encoding": self._result.encoding,
            "has_header": self._result.has_header,
            "columns": len(self._result.columns or []),
            "confidence": self._result.confidence,
            "status": self._detection_status,
            "is_multiline": self._result.is_multiline,
        }

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
