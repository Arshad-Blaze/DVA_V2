"""Processing controller — bridges processing service to UI (Sprint 6B)."""

from typing import Any, Dict, List
from ui.services.processing_service import ProcessingService
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import ExecutionState, ExecutionResult, OperationLog


class ProcessingController:
    """Controls Execution Center operations from the UI."""

    def __init__(self, svc: ProcessingService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def start(self) -> None:
        if self._svc.state in (ExecutionState.PENDING, ExecutionState.CANCELLED, ExecutionState.FAILED):
            self._svc.start()
            self._notify.info("Processing started")
        else:
            self._notify.warning("Cannot start: already running or completed")

    def pause(self) -> None:
        self._svc.pause()
        self._notify.info("Processing paused")

    def resume(self) -> None:
        self._svc.resume()
        self._notify.info("Processing resumed")

    def cancel(self) -> None:
        self._svc.cancel()
        self._notify.warning("Processing cancelled")

    def retry(self) -> None:
        self._svc.retry()
        self._notify.info("Ready to retry")

    @property
    def state(self) -> ExecutionState:
        return self._svc.state

    @property
    def is_running(self) -> bool:
        return self._svc.is_running

    @property
    def is_completed(self) -> bool:
        return self._svc.is_completed

    @property
    def is_paused(self) -> bool:
        return self._svc.is_paused

    @property
    def progress(self) -> float:
        return self._svc.progress

    @property
    def current_stage_index(self) -> int:
        return self._svc.current_stage_index

    @property
    def current_stage_label(self) -> str:
        return self._svc.current_stage_label

    @property
    def rows_processed(self) -> int:
        return self._svc.rows_processed

    @property
    def elapsed_seconds(self) -> float:
        return self._svc.elapsed_seconds

    @property
    def rows_per_sec(self) -> float:
        return self._svc.rows_per_sec

    @property
    def pipeline_stages(self) -> List[Dict[str, Any]]:
        return self._svc.pipeline_stages

    @property
    def logs(self) -> List[OperationLog]:
        return self._svc.logs

    @property
    def recent_logs(self) -> List[OperationLog]:
        return self._svc.recent_logs

    @property
    def metrics(self) -> Dict[str, Any]:
        return self._svc.metrics

    @property
    def performance_data(self) -> Dict[str, List[float]]:
        return self._svc.performance_data

    @property
    def results_summary(self) -> Dict[str, Any]:
        return self._svc.results_summary

    @property
    def execution_result(self) -> ExecutionResult:
        return self._svc.execution_result
