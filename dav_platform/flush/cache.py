"""Flush Layer — Cache Manager."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


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
                logger.warning("Failed to clear cache '%s'", key, exc_info=True)
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
                logger.warning("Failed to clear cache key '%s'", key, exc_info=True)
            del self._caches[key]
            return True
        return False

    @property
    def cache_count(self) -> int:
        return len(self._caches)
