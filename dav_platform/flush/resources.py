"""Flush Layer — Resource Manager."""

import gc
from typing import Any, Dict, List, Optional

from dav_platform.flush.exceptions import ResourceCleanupError


class ResourceManager:
    """Manages cleanup of runtime resources.

    Handles memory, streaming buffers, thread pools, file handles.
    """

    def cleanup_memory(self, dry_run: bool = False) -> Dict[str, Any]:
        """Release memory by running garbage collection."""
        if dry_run:
            return {"action": "memory_cleanup", "dry_run": True, "status": "skipped"}
        try:
            gc.collect()
            return {"action": "memory_cleanup", "status": "completed"}
        except Exception as e:
            raise ResourceCleanupError(f"Memory cleanup failed: {e}")

    def cleanup_buffers(self, buffers: Optional[List[Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Clear streaming and chunk buffers."""
        if dry_run:
            return {"action": "buffer_cleanup", "dry_run": True, "status": "skipped"}
        count = 0
        if buffers:
            buffers.clear()
            count = 1
        return {"action": "buffer_cleanup", "buffers_cleared": count, "status": "completed"}

    def cleanup_dataframes(self, dataframes: Optional[List[Any]] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Drop references to temporary DataFrames."""
        if dry_run:
            return {"action": "dataframe_cleanup", "dry_run": True, "status": "skipped"}
        count = 0
        if dataframes:
            count = len(dataframes)
            dataframes.clear()
        return {"action": "dataframe_cleanup", "dataframes_dropped": count, "status": "completed"}
