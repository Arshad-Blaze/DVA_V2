"""Flush Layer — Audit Trail."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class AuditTrail:
    """Persists audit information about the execution lifecycle."""

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []
        self._execution_id: str = ""
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    def set_execution_id(self, exec_id: str) -> None:
        self._execution_id = exec_id

    def start(self) -> None:
        self._start_time = datetime.now(timezone.utc)

    def end(self) -> None:
        self._end_time = datetime.now(timezone.utc)

    def record(self, entry: Dict[str, Any]) -> None:
        self._entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **entry,
        })

    def record_layer(self, layer: str, status: str, duration: float = 0.0) -> None:
        self.record({
            "type": "layer_execution",
            "layer": layer,
            "status": status,
            "duration_seconds": duration,
        })

    def record_cleanup(self, action: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.record({
            "type": "cleanup",
            "action": action,
            "status": status,
            **(details or {}),
        })

    def record_error(self, source: str, message: str) -> None:
        self.record({
            "type": "error",
            "source": source,
            "message": message,
        })

    def record_warning(self, source: str, message: str) -> None:
        self.record({
            "type": "warning",
            "source": source,
            "message": message,
        })

    def build(self) -> Dict[str, Any]:
        return {
            "execution_id": self._execution_id,
            "start_time": self._start_time.isoformat() if self._start_time else "",
            "end_time": self._end_time.isoformat() if self._end_time else "",
            "entries": list(self._entries),
            "entry_count": len(self._entries),
        }
