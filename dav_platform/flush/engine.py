"""Flush Layer — Engine.

Orchestrates the execution lifecycle: cleanup, metrics, audit, summary.
"""

import time
from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import (
    CleanupSummary,
    ExecutionResult,
    ExportManifest,
    FlushConfig,
    FlushResult,
    OutputArtifacts,
)
from dav_platform.flush.audit import AuditTrail
from dav_platform.flush.cache import CacheManager
from dav_platform.flush.cleanup import CleanupManager
from dav_platform.flush.connections import ConnectionCleanup
from dav_platform.flush.metrics import MetricsCollector
from dav_platform.flush.resources import ResourceManager
from dav_platform.flush.session import SessionCleanup
from dav_platform.flush.summary import LifecycleSummaryBuilder


class FlushEngine:
    """Execution lifecycle manager.

    Owns cleanup, resource release, metrics, audit, and lifecycle summary.
    Performs NO business logic, NO validation, NO aggregation.
    """

    def __init__(self, config: Optional[FlushConfig] = None):
        self._config = config or FlushConfig()
        self._cleanup = CleanupManager()
        self._resources = ResourceManager()
        self._connections = ConnectionCleanup()
        self._cache = CacheManager()
        self._session = SessionCleanup()
        self._metrics = MetricsCollector()
        self._audit = AuditTrail()
        self._summary_builder = LifecycleSummaryBuilder()

    @property
    def config(self) -> FlushConfig:
        return self._config

    @property
    def cleanup(self) -> CleanupManager:
        return self._cleanup

    @property
    def connections(self) -> ConnectionCleanup:
        return self._connections

    @property
    def cache(self) -> CacheManager:
        return self._cache

    @property
    def session(self) -> SessionCleanup:
        return self._session

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    @property
    def audit(self) -> AuditTrail:
        return self._audit

    def flush(
        self,
        execution_result: Optional[ExecutionResult] = None,
        output_artifacts: Optional[OutputArtifacts] = None,
        export_manifest: Optional[ExportManifest] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> FlushResult:
        """Execute the complete flush lifecycle.

        Args:
            execution_result: Result from the Operation layer.
            output_artifacts: Artifacts from the Output layer.
            export_manifest: Manifest from the Output layer.
            context: Optional additional context.

        Returns:
            FlushResult with cleanup summary, metrics, and lifecycle summary.
        """
        start = time.time()
        all_warnings: List[str] = []
        all_errors: List[str] = []

        self._audit.start()

        execution_status = "success"
        if execution_result:
            if execution_result.failed:
                execution_status = "failed"
            elif execution_result.warnings:
                execution_status = "partial"
            if execution_result.metadata:
                self._metrics.record_layer_time(
                    "execution", execution_result.metadata.execution_duration
                )

        cleanup_summary = self._execute_cleanup(all_warnings, all_errors)

        self._audit.end()

        total_duration = time.time() - start
        self._metrics.record_memory(0.0, 0.0)

        if output_artifacts and output_artifacts.statistics:
            self._metrics.add_exports(output_artifacts.statistics.total_files_generated)

        if export_manifest:
            self._metrics.add_exports(export_manifest.total_files)

        execution_metrics = self._metrics.build(total_execution_time=total_duration)

        lifecycle_summary = self._summary_builder.build(
            execution_status=execution_status,
            total_duration=total_duration,
            cleanup_summary=cleanup_summary,
            metrics=execution_metrics,
            artifacts=output_artifacts,
            warnings=all_warnings,
            errors=all_errors,
        )

        self._audit.record({
            "type": "flush_complete",
            "execution_status": execution_status,
            "duration_seconds": total_duration,
            "cleanup_status": "complete" if cleanup_summary and not cleanup_summary.errors else "partial" if cleanup_summary else "skipped",
        })

        return FlushResult(
            success=len(all_errors) == 0,
            cleanup=cleanup_summary,
            metrics=execution_metrics,
            summary=lifecycle_summary,
            warnings=all_warnings,
            errors=all_errors,
        )

    def _execute_cleanup(
        self, warnings: List[str], errors: List[str]
    ) -> CleanupSummary:
        dry_run = self._config.dry_run
        details: Dict[str, Any] = {}

        retain_temp = None
        if self._config.retain_temp_files:
            retain_temp = self._config.temp_directories

        try:
            result = self._cleanup.delete_temp_files(
                retain=retain_temp, dry_run=dry_run
            )
            details["temp_files"] = result
            if "errors" in result:
                for err in result["errors"]:
                    errors.append(f"Temp file cleanup: {err}")
        except Exception as e:
            warnings.append(f"Temp file cleanup failed: {e}")

        try:
            result = self._cleanup.delete_temp_dirs(
                retain=retain_temp, dry_run=dry_run
            )
            details["temp_dirs"] = result
            if "errors" in result:
                for err in result["errors"]:
                    errors.append(f"Temp dir cleanup: {err}")
        except Exception as e:
            warnings.append(f"Temp dir cleanup failed: {e}")

        if self._config.delete_exports:
            try:
                result = self._cleanup.delete_exports(dry_run=dry_run)
                details["exports"] = result
            except Exception as e:
                warnings.append(f"Export cleanup failed: {e}")

        try:
            result = self._resources.cleanup_memory(dry_run=dry_run)
            details["memory"] = result
        except Exception as e:
            warnings.append(f"Memory cleanup failed: {e}")

        try:
            result = self._connections.close_all(dry_run=dry_run)
            details["connections"] = result
            if "errors" in result:
                for err in result["errors"]:
                    errors.append(f"Connection cleanup: {err}")
        except Exception as e:
            warnings.append(f"Connection cleanup failed: {e}")

        preserve_caches = None
        if self._config.retain_caches:
            preserve_caches = self._config.cache_keys
        try:
            result = self._cache.clear_all(preserve=preserve_caches, dry_run=dry_run)
            details["caches"] = result
        except Exception as e:
            warnings.append(f"Cache cleanup failed: {e}")

        try:
            result = self._session.reset_all(dry_run=dry_run)
            details["sessions"] = result
        except Exception as e:
            warnings.append(f"Session cleanup failed: {e}")

        files_deleted = (
            details.get("temp_files", {}).get("files_deleted", 0)
            + details.get("temp_dirs", {}).get("dirs_deleted", 0)
        )
        connections_closed = details.get("connections", {}).get("connections_closed", 0)
        caches_cleared = details.get("caches", {}).get("caches_cleared", 0)
        sessions_reset = (
            details.get("sessions", {}).get("trackers_reset", 0)
            + details.get("sessions", {}).get("contexts_reset", 0)
        )
        memory_released = details.get("memory", {}).get("status") == "completed"

        for w in self._config.metadata.get("_warnings", []):
            warnings.append(w)

        return CleanupSummary(
            files_deleted=files_deleted,
            connections_closed=connections_closed,
            caches_cleared=caches_cleared,
            sessions_reset=sessions_reset,
            memory_released=memory_released,
            warnings=warnings,
            errors=errors,
            details=details,
        )

    def get_audit_trail(self) -> Dict[str, Any]:
        return self._audit.build()
