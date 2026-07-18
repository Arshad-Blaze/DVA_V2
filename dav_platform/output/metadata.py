"""Output Layer — Metadata Collector."""

from typing import Any, Dict, List


class OutputMetadataCollector:
    """Collects metadata about the output generation process."""

    def __init__(self):
        self._data: Dict[str, Any] = {
            "export_duration_seconds": 0.0,
            "rows_exported": 0,
            "sheets_created": 0,
            "files_generated": [],
            "warnings": [],
            "skipped_outputs": [],
            "version": "2.0",
        }

    def set_duration(self, seconds: float):
        self._data["export_duration_seconds"] = seconds

    def add_rows(self, count: int):
        self._data["rows_exported"] += count

    def add_sheets(self, count: int):
        self._data["sheets_created"] += count

    def add_file(self, file_path: str, file_format: str):
        self._data["files_generated"].append({"path": file_path, "format": file_format})

    def add_warning(self, message: str):
        self._data["warnings"].append(message)

    def add_skipped(self, name: str, reason: str = ""):
        self._data["skipped_outputs"].append({"name": name, "reason": reason})

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._data)
