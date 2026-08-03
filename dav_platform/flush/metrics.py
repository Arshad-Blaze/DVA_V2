"""Flush Layer — Metrics Collector."""

from typing import Dict

from dav_platform.core.contracts import ExecutionMetrics


class MetricsCollector:
    """Collects execution metrics across all layers."""

    def __init__(self):
        self._layer_timings: Dict[str, float] = {}
        self._rows_processed = 0
        self._files_processed = 0
        self._chunk_count = 0
        self._export_count = 0
        self._validation_rules_passed = 0
        self._validation_rules_failed = 0
        self._retry_count = 0
        self._memory_usage_mb = 0.0
        self._peak_memory_mb = 0.0

    def record_layer_time(self, layer: str, seconds: float) -> None:
        self._layer_timings[layer] = seconds

    def add_rows_processed(self, count: int) -> None:
        self._rows_processed += count

    def add_files_processed(self, count: int = 1) -> None:
        self._files_processed += count

    def add_chunks(self, count: int = 1) -> None:
        self._chunk_count += count

    def add_exports(self, count: int = 1) -> None:
        self._export_count += count

    def set_validation_results(self, passed: int, failed: int) -> None:
        self._validation_rules_passed = passed
        self._validation_rules_failed = failed

    def add_retries(self, count: int = 1) -> None:
        self._retry_count += count

    def record_memory(self, current_mb: float, peak_mb: float) -> None:
        self._memory_usage_mb = current_mb
        self._peak_memory_mb = max(self._peak_memory_mb, peak_mb)

    def build(self, total_execution_time: float = 0.0) -> ExecutionMetrics:
        total = self._validation_rules_passed + self._validation_rules_failed
        success_rate = 100.0 if total == 0 else (self._validation_rules_passed / total * 100)
        failure_rate = 0.0 if total == 0 else (self._validation_rules_failed / total * 100)
        return ExecutionMetrics(
            total_execution_time_seconds=total_execution_time,
            layer_timings=dict(self._layer_timings),
            rows_processed=self._rows_processed,
            files_processed=self._files_processed,
            memory_usage_mb=self._memory_usage_mb,
            peak_memory_mb=self._peak_memory_mb,
            chunk_count=self._chunk_count,
            export_count=self._export_count,
            validation_rules_passed=self._validation_rules_passed,
            validation_rules_failed=self._validation_rules_failed,
            retry_count=self._retry_count,
            success_rate=success_rate,
            failure_rate=failure_rate,
        )
