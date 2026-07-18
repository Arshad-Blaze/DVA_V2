"""Flush Layer — Cache Manager."""

from typing import Any, Dict, List, Optional

from dav_platform.flush.exceptions import CacheCleanupError


class CacheManager:
    """Manages in-memory, session, and lookup caches."""

    def __init__(self):
        self._caches: Dict[str, Any] = {}

    def register(self, key: str, cache: Any) -> None:
        self._caches[key] = cache

    def clear_all(self, preserve: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "cache_cleanup", "dry_run": True, "status": "skipped", "count": len(self._caches)}
        cleared = 0
        preserve = preserve or []
        keys = list(self._caches.keys())
        for key in keys:
            if key in preserve:
                continue
            cache = self._caches[key]
            try:
                if hasattr(cache, "clear"):
                    cache.clear()
                elif isinstance(cache, dict):
                    cache.clear()
                elif isinstance(cache, list):
                    cache.clear()
                cleared += 1
            except Exception:
                pass
            if key not in preserve:
                del self._caches[key]
        return {"action": "cache_cleanup", "caches_cleared": cleared, "status": "completed"}

    def clear_key(self, key: str) -> bool:
        if key in self._caches:
            cache = self._caches[key]
            try:
                if hasattr(cache, "clear"):
                    cache.clear()
                elif isinstance(cache, (dict, list)):
                    cache.clear()
            except Exception:
                pass
            del self._caches[key]
            return True
        return False

    @property
    def cache_count(self) -> int:
        return len(self._caches)
