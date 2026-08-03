import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Timer:
    def __init__(self, label: str = ""):
        self._label = label
        self._start: float = 0
        self._elapsed: float = 0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._elapsed = time.perf_counter() - self._start
        if self._label:
            logger.debug("Timer[%s] took %.2fms", self._label, self.elapsed_ms)

    @property
    def elapsed_ms(self) -> float:
        return self._elapsed * 1000


class SimpleCache:
    def __init__(self, ttl_seconds: float = 5.0):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() - self._timestamps.get(key, 0) < self._ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._timestamps[key]
        return None

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def invalidate_all(self) -> None:
        self._cache.clear()
        self._timestamps.clear()


class PerformanceService:
    def __init__(self):
        self._caches: Dict[str, SimpleCache] = {}
        self._metrics: Dict[str, list] = {}
        self._startup_time: Optional[float] = None

    def get_cache(self, name: str, ttl: float = 5.0) -> SimpleCache:
        if name not in self._caches:
            self._caches[name] = SimpleCache(ttl)
        return self._caches[name]

    def record_startup(self) -> None:
        self._startup_time = time.time()

    @property
    def startup_time_ms(self) -> float:
        if self._startup_time:
            return (time.time() - self._startup_time) * 1000
        return 0

    def record_metric(self, name: str, value: float) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)
        if len(self._metrics[name]) > 100:
            self._metrics[name] = self._metrics[name][-100:]

    def get_metrics(self, name: str) -> list:
        return list(self._metrics.get(name, []))

    def get_all_metrics(self) -> Dict[str, list]:
        return dict(self._metrics)

    def reset_metrics(self) -> None:
        self._metrics.clear()

    def invalidate_all_caches(self) -> None:
        for cache in self._caches.values():
            cache.invalidate_all()
