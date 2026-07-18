"""Flush Layer — Lifecycle Summary Builder."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import (
    CleanupSummary,
    ExecutionMetrics,
    LifecycleSummary,
    OutputArtifacts,
)


class LifecycleSummaryBuilder:
    """Builds final execution lifecycle summary."""

    def build(
        self,
        execution_status: str,
        total_duration: float,
        cleanup_summary: Optional[CleanupSummary] = None,
        metrics: Optional[ExecutionMetrics] = None,
        artifacts: Optional[OutputArtifacts] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
    ) -> LifecycleSummary:
        generated_outputs = []
        if artifacts:
            generated_outputs.extend(artifacts.excel_files or [])
            generated_outputs.extend(artifacts.csv_files or [])
            generated_outputs.extend(artifacts.json_files or [])

        cleanup_status = "complete"
        if cleanup_summary:
            if cleanup_summary.errors:
                cleanup_status = "partial"
        else:
            cleanup_status = "skipped"

        resource_release = "All resources released"
        if cleanup_summary and cleanup_summary.errors:
            resource_release = f"Resources released with {len(cleanup_summary.errors)} error(s)"

        return LifecycleSummary(
            execution_status=execution_status,
            total_duration_seconds=total_duration,
            warnings=warnings or [],
            errors=errors or [],
            generated_outputs=generated_outputs,
            cleanup_status=cleanup_status,
            resource_release_summary=resource_release,
        )
