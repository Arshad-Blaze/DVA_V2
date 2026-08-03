"""Flush Layer — Connection Cleanup."""

from typing import Any, Dict, List


class ConnectionCleanup:
    """Closes network connections and remote resources."""

    def __init__(self):
        self._connections: List[Dict[str, Any]] = []

    def register(self, conn: Dict[str, Any]) -> None:
        self._connections.append(conn)

    def close_all(self, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "connection_cleanup", "dry_run": True, "status": "skipped", "count": len(self._connections)}
        closed = 0
        errors = []
        for conn in self._connections:
            try:
                conn_type = conn.get("type", "unknown")
                handle = conn.get("handle")
                if handle is not None:
                    try:
                        if hasattr(handle, "close"):
                            handle.close()
                        closed += 1
                    except Exception as e:
                        errors.append(f"Failed to close {conn_type}: {e}")
                else:
                    closed += 1
            except Exception as e:
                errors.append(str(e))
        self._connections.clear()
        result = {"action": "connection_cleanup", "connections_closed": closed, "status": "completed"}
        if errors:
            result["errors"] = errors
        return result

    @property
    def count(self) -> int:
        return len(self._connections)
