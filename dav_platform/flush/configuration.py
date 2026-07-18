"""Flush Layer — Configuration Builder."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import FlushConfig


class FlushConfigBuilder:
    """Builder for FlushConfig objects."""

    def __init__(self):
        self._retain_temp_files = False
        self._retain_logs = False
        self._retain_caches = False
        self._delete_exports = False
        self._archive_reports = False
        self._verbose = False
        self._dry_run = False
        self._temp_directories: List[str] = []
        self._cache_keys: List[str] = []
        self._metadata: Dict[str, Any] = {}

    def retain_temp_files(self, val: bool = True) -> "FlushConfigBuilder":
        self._retain_temp_files = val
        return self

    def retain_logs(self, val: bool = True) -> "FlushConfigBuilder":
        self._retain_logs = val
        return self

    def retain_caches(self, val: bool = True) -> "FlushConfigBuilder":
        self._retain_caches = val
        return self

    def delete_exports(self, val: bool = True) -> "FlushConfigBuilder":
        self._delete_exports = val
        return self

    def archive_reports(self, val: bool = True) -> "FlushConfigBuilder":
        self._archive_reports = val
        return self

    def verbose(self, val: bool = True) -> "FlushConfigBuilder":
        self._verbose = val
        return self

    def dry_run(self, val: bool = True) -> "FlushConfigBuilder":
        self._dry_run = val
        return self

    def add_temp_directory(self, path: str) -> "FlushConfigBuilder":
        self._temp_directories.append(path)
        return self

    def add_cache_key(self, key: str) -> "FlushConfigBuilder":
        self._cache_keys.append(key)
        return self

    def metadata(self, key: str, value: Any) -> "FlushConfigBuilder":
        self._metadata[key] = value
        return self

    def build(self) -> FlushConfig:
        return FlushConfig(
            retain_temp_files=self._retain_temp_files,
            retain_logs=self._retain_logs,
            retain_caches=self._retain_caches,
            delete_exports=self._delete_exports,
            archive_reports=self._archive_reports,
            verbose=self._verbose,
            dry_run=self._dry_run,
            temp_directories=self._temp_directories,
            cache_keys=self._cache_keys,
            metadata=self._metadata,
        )


def build_flush_config(
    retain_temp_files: bool = False,
    retain_logs: bool = False,
    dry_run: bool = False,
    **kwargs,
) -> FlushConfig:
    builder = FlushConfigBuilder()
    if retain_temp_files:
        builder.retain_temp_files()
    if retain_logs:
        builder.retain_logs()
    if dry_run:
        builder.dry_run()
    return builder.build()
