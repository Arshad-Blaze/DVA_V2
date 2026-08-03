"""Flush Layer — Session Cleanup."""

from typing import Any, Dict, List


class SessionCleanup:
    """Resets execution context, session state, progress trackers."""

    def __init__(self):
        self._trackers: List[Dict[str, Any]] = []
        self._contexts: List[Dict[str, Any]] = []

    def register_tracker(self, tracker: Dict[str, Any]) -> None:
        self._trackers.append(tracker)

    def register_context(self, context: Dict[str, Any]) -> None:
        self._contexts.append(context)

    def reset_all(self, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "session_cleanup", "dry_run": True, "status": "skipped",
                    "trackers": len(self._trackers), "contexts": len(self._contexts)}
        tracker_count = len(self._trackers)
        context_count = len(self._contexts)
        for t in self._trackers:
            t.clear()
        for c in self._contexts:
            c.clear()
        self._trackers.clear()
        self._contexts.clear()
        return {"action": "session_cleanup", "trackers_reset": tracker_count,
                "contexts_reset": context_count, "status": "completed"}
