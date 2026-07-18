"""Output Layer — Export Manifest Builder."""

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import ExportManifest


class ManifestBuilder:
    """Builds an ExportManifest of all generated files."""

    def __init__(self):
        self._files: List[Dict[str, Any]] = []
        self._start_time: Optional[float] = None

    def start(self) -> "ManifestBuilder":
        self._start_time = time.time()
        return self

    def add_file(
        self,
        file_path: str,
        file_format: str,
        rows: int = 0,
        sheets: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ManifestBuilder":
        try:
            size = os.path.getsize(file_path)
        except OSError:
            size = 0
        self._files.append({
            "file_path": os.path.abspath(file_path),
            "format": file_format,
            "size_bytes": size,
            "rows": rows,
            "sheets": sheets,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        })
        return self

    def build(self) -> ExportManifest:
        duration = 0.0
        if self._start_time is not None:
            duration = time.time() - self._start_time
        total_size = sum(f.get("size_bytes", 0) for f in self._files)
        return ExportManifest(
            files=list(self._files),
            total_files=len(self._files),
            total_size_bytes=total_size,
            export_duration_seconds=duration,
            export_timestamp=datetime.now(timezone.utc).isoformat(),
        )
