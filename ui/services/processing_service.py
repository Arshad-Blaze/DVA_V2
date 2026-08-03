"""Processing service — Execution Center (Sprint 6B).

Simulates execution lifecycle: progress, logs, metrics, performance, results.
Never processes data — UI only monitors and controls.
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from dav_platform.core.contracts import (
    ExecutionState,
    ExecutionStepResult,
    OperationLog,
    ExecutionMetadata,
    ExecutionResult,
    CanonicalDataset,
)
from dav_platform.processing.engine import ProcessingEngine
from dav_platform.processing.configuration import build_config

LOG_LEVELS = ["info", "warning", "error", "success"]

STAGE_LABELS = ["Load", "Aggregate", "Calculate", "Validate", "Generate Reports", "Export"]

SIMULATION_DELAYS = [2.0, 3.0, 2.5, 3.5, 2.0, 1.5]  # seconds per stage


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class ProcessingService:
    """Manages execution lifecycle.

    Simulates stage progression, log generation, and metrics collection.
    Never processes data — UI only monitors.
    """

    def __init__(self, op_svc=None, dataset: Optional[CanonicalDataset] = None):
        self._op = op_svc
        self._dataset: Optional[CanonicalDataset] = dataset
        self._state: ExecutionState = ExecutionState.PENDING
        self._current_stage: int = 0
        self._progress: float = 0.0
        self._rows_processed: int = 0
        self._elapsed: float = 0.0
        self._logs: List[OperationLog] = []
        self._step_results: List[ExecutionStepResult] = []
        self._metrics: Dict[str, Any] = self._default_metrics()
        self._timer: Optional[threading.Thread] = None
        self._running: bool = False
        self._start_time: Optional[float] = None
        self._paused: bool = False
        self._on_change: Optional[Callable] = None

        # Initialize step results
        for i, label in enumerate(STAGE_LABELS):
            self._step_results.append(ExecutionStepResult(
                step_number=i + 1,
                action=label,
                state=ExecutionState.PENDING,
            ))

    def load_dataset(self, dataset: Optional[CanonicalDataset]) -> None:
        """Attach a canonical dataset for real backend processing."""
        self._dataset = dataset

    def _default_metrics(self) -> Dict[str, Any]:
        return {
            "memory_mb": 0.0,
            "peak_memory_mb": 0.0,
            "cpu_pct": 0.0,
            "streaming": True,
            "chunks": 0,
            "rows": 0,
            "files": 0,
            "aggregations": 0,
            "calculations": 0,
            "validation_queue": 0,
            "rows_per_sec": 0.0,
            "memory_trend": [0] * 10,
            "cpu_trend": [0] * 10,
        }

    # ── Lifecycle ────────────────────────────────────────────

    @property
    def state(self) -> ExecutionState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == ExecutionState.RUNNING

    @property
    def is_completed(self) -> bool:
        return self._state == ExecutionState.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self._state == ExecutionState.FAILED

    @property
    def is_cancelled(self) -> bool:
        return self._state == ExecutionState.CANCELLED

    @property
    def is_paused(self) -> bool:
        return self._paused

    def start(self) -> None:
        if self._state not in (ExecutionState.PENDING, ExecutionState.CANCELLED, ExecutionState.FAILED):
            return
        self._state = ExecutionState.RUNNING
        self._current_stage = 0
        self._progress = 0.0
        self._rows_processed = 0
        self._elapsed = 0.0
        self._logs = []
        self._metrics = self._default_metrics()
        self._start_time = time.time()
        self._paused = False
        self._running = True

        # Reset step results
        for i, label in enumerate(STAGE_LABELS):
            self._step_results[i] = ExecutionStepResult(
                step_number=i + 1, action=label, state=ExecutionState.PENDING,
            )

        self._add_log("info", "Execution started", "Initializing processing pipeline...")
        self._timer = threading.Thread(target=self._execute, daemon=True)
        self._timer.start()
        self._notify()

    def _execute(self) -> None:
        if self._dataset is not None:
            self._run_backend()
        else:
            self._simulate()

    def _run_backend(self) -> None:
        """Execute the real ProcessingEngine against the loaded dataset."""
        dataset = self._dataset
        context = None
        if self._op is not None and hasattr(self._op, "operation_context"):
            try:
                context = self._op.operation_context
            except Exception:
                context = None

        self._step_results[0].state = ExecutionState.RUNNING
        self._current_stage = 0
        self._add_log("info", "Load", "Loading canonical dataset...")
        self._notify()

        try:
            config = build_config(dataset=dataset, context=context)
            engine = ProcessingEngine()
            result = engine.process(dataset, config=config, context=context)

            if result is None or getattr(result, "errors", None):
                err_msg = ""
                if result is not None:
                    err_msg = "; ".join(getattr(result, "errors", []) or [])
                raise RuntimeError(err_msg or "Processing failed")

            self._rows_processed = int(getattr(result, "row_count", 0) or 0)
            self._elapsed = getattr(result, "elapsed_seconds", 0.0) or 0.0
            self._progress = 100.0
            self._metrics = self._default_metrics()
            self._metrics["rows"] = self._rows_processed
            self._metrics["chunks"] = 1
            self._metrics["memory_mb"] = round(getattr(result, "memory_peak_mb", 0.0) or 0.0, 1)
            self._metrics["peak_memory_mb"] = self._metrics["memory_mb"]
            self._metrics["rows_per_sec"] = round(self._rows_processed / max(self._elapsed, 0.1), 1)

            for i in range(len(self._step_results)):
                self._step_results[i].state = ExecutionState.COMPLETED
                self._step_results[i].elapsed_seconds = round(self._elapsed / max(len(self._step_results), 1), 1)
            self._current_stage = len(self._step_results) - 1

            self._state = ExecutionState.COMPLETED
            self._add_log("success", "Execution", f"Processing completed in {self._elapsed:.1f}s")
        except Exception as exc:
            self._state = ExecutionState.FAILED
            self._add_log("error", "Execution", f"Processing failed: {exc}")
        finally:
            self._running = False
            self._notify()

    def _simulate(self) -> None:
        for stage_idx in range(len(STAGE_LABELS)):
            if not self._running or self._state == ExecutionState.CANCELLED:
                return

            self._current_stage = stage_idx
            self._step_results[stage_idx].state = ExecutionState.RUNNING
            self._add_log("info", STAGE_LABELS[stage_idx], f"Starting {STAGE_LABELS[stage_idx]} stage...")

            delay = SIMULATION_DELAYS[stage_idx]
            steps = 20
            for s in range(steps):
                if not self._running or self._state == ExecutionState.CANCELLED:
                    return
                while self._paused:
                    time.sleep(0.1)
                    if not self._running:
                        return

                time.sleep(delay / steps)
                stage_progress = (s + 1) / steps
                self._progress = (stage_idx + stage_progress) / len(STAGE_LABELS) * 100
                self._elapsed = time.time() - self._start_time
                self._rows_processed = int(1250 * self._progress / 100)
                self._metrics["rows"] = self._rows_processed
                self._metrics["rows_per_sec"] = round(self._rows_processed / max(self._elapsed, 0.1), 1)
                self._metrics["memory_mb"] = round(64 + (stage_idx * 32) + (s * 3), 1)
                self._metrics["peak_memory_mb"] = max(self._metrics["peak_memory_mb"], self._metrics["memory_mb"])
                self._metrics["cpu_pct"] = min(95, 40 + stage_idx * 10 + s)
                self._metrics["memory_trend"] = self._metrics["memory_trend"][1:] + [self._metrics["memory_mb"]]
                self._metrics["cpu_trend"] = self._metrics["cpu_trend"][1:] + [self._metrics["cpu_pct"]]
                self._metrics["chunks"] = int(self._rows_processed / 10000) + 1

                if s == steps - 1:
                    self._metrics["aggregations"] = stage_idx >= 1
                    self._metrics["calculations"] = stage_idx >= 2
                    self._metrics["validation_queue"] = 10 if stage_idx >= 3 else 0

                self._notify()

            self._step_results[stage_idx].state = ExecutionState.COMPLETED
            self._step_results[stage_idx].elapsed_seconds = round(delay, 1)
            self._add_log("success", STAGE_LABELS[stage_idx], f"{STAGE_LABELS[stage_idx]} completed in {delay:.1f}s")

        # All stages complete
        self._state = ExecutionState.COMPLETED
        self._progress = 100.0
        self._elapsed = time.time() - self._start_time
        self._metrics["rows_per_sec"] = round(self._rows_processed / max(self._elapsed, 0.1), 1)
        self._add_log("success", "Execution", f"Processing completed in {self._elapsed:.1f}s")
        self._running = False
        self._notify()

    def pause(self) -> None:
        if self._state == ExecutionState.RUNNING:
            self._paused = True
            self._add_log("warning", "Execution", "Processing paused by user")
            self._notify()

    def resume(self) -> None:
        if self._paused:
            self._paused = False
            self._add_log("info", "Execution", "Processing resumed")
            self._notify()

    def cancel(self) -> None:
        if self._state == ExecutionState.RUNNING or self._paused:
            self._state = ExecutionState.CANCELLED
            self._running = False
            self._paused = False
            self._step_results[self._current_stage].state = ExecutionState.CANCELLED
            self._add_log("warning", "Execution", "Processing cancelled by user")
            self._notify()

    def retry(self) -> None:
        self._state = ExecutionState.PENDING
        self._running = False
        self._paused = False
        self._current_stage = 0
        self._progress = 0.0
        self._add_log("info", "Execution", "Ready to retry")
        self._notify()

    def _add_log(self, level: str, action: str, message: str) -> None:
        self._logs.append(OperationLog(
            timestamp=_timestamp(),
            level=level,
            step_number=self._current_stage + 1 if self._current_stage < len(STAGE_LABELS) else None,
            action=action,
            message=message,
        ))

    # ── Progress ─────────────────────────────────────────────

    @property
    def progress(self) -> float:
        return round(self._progress, 1)

    @property
    def current_stage_index(self) -> int:
        return self._current_stage

    @property
    def current_stage_label(self) -> str:
        if self._current_stage < len(STAGE_LABELS):
            return STAGE_LABELS[self._current_stage]
        return "Complete"

    @property
    def rows_processed(self) -> int:
        return self._rows_processed

    @property
    def elapsed_seconds(self) -> float:
        return round(self._elapsed, 1)

    @property
    def rows_per_sec(self) -> float:
        return round(self._metrics["rows_per_sec"], 1)

    # ── Pipeline ─────────────────────────────────────────────

    @property
    def pipeline_stages(self) -> List[Dict[str, Any]]:
        stages = []
        for i, label in enumerate(STAGE_LABELS):
            result = self._step_results[i] if i < len(self._step_results) else None
            state = result.state if result else ExecutionState.PENDING
            stages.append({
                "id": label.lower().replace(" ", "_"),
                "label": label,
                "state": state.value,
                "elapsed": round(result.elapsed_seconds, 1) if result else 0.0,
            })
        return stages

    # ── Logs ─────────────────────────────────────────────────

    @property
    def logs(self) -> List[OperationLog]:
        return list(self._logs)

    @property
    def recent_logs(self) -> List[OperationLog]:
        return list(self._logs[-50:])  # last 50

    # ── Metrics ──────────────────────────────────────────────

    @property
    def metrics(self) -> Dict[str, Any]:
        return dict(self._metrics)

    @property
    def performance_data(self) -> Dict[str, List[float]]:
        return {
            "memory_trend": list(self._metrics.get("memory_trend", [])),
            "cpu_trend": list(self._metrics.get("cpu_trend", [])),
        }

    # ── Results ──────────────────────────────────────────────

    @property
    def results_summary(self) -> Dict[str, Any]:
        return {
            "rows_processed": self._rows_processed,
            "stores": 45,
            "upcs": 892,
            "categories": 12,
            "brands": 64,
            "departments": 8,
            "aggregations": "sum, count, mean",
            "calculations": "total_sales, avg_price, item_count",
            "warnings": 2,
            "errors": 0,
            "state": self._state.value,
        }

    # ── Execution Result ─────────────────────────────────────

    @property
    def execution_result(self) -> ExecutionResult:
        return ExecutionResult(
            state=self._state,
            step_results=list(self._step_results),
            metadata=ExecutionMetadata(
                workflow=self._get_workflow(),
                total_steps=len(STAGE_LABELS),
                completed_steps=sum(1 for r in self._step_results if r.state == ExecutionState.COMPLETED),
                failed_steps=sum(1 for r in self._step_results if r.state == ExecutionState.FAILED),
                skipped_steps=sum(1 for r in self._step_results if r.state == ExecutionState.SKIPPED),
                execution_duration=self._elapsed,
                outcome=self._state.value,
            ),
            logs=list(self._logs),
        )

    def _get_workflow(self) -> str:
        if self._op and hasattr(self._op, '_req'):
            req = self._op._req
            if hasattr(req, 'recommendation'):
                return req.recommendation.get("workflow", "")
        return "Aggregate + Calculate"

    # ── Events ──────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
