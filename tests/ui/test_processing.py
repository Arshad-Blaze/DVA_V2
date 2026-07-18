"""UI Tests — Execution Center (Sprint 6B)."""

import time
import pytest
from ui.services.processing_service import ProcessingService
from ui.controllers.processing_controller import ProcessingController
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import ExecutionState, OperationLog, ExecutionStepResult


class TestProcessingService:
    def test_default_state(self):
        svc = ProcessingService()
        assert svc.state == ExecutionState.PENDING
        assert svc.is_running is False
        assert svc.is_completed is False
        assert svc.is_paused is False
        assert svc.progress == 0.0

    def test_pipeline_stages_pending(self):
        svc = ProcessingService()
        stages = svc.pipeline_stages
        assert len(stages) == 6
        assert stages[0]["label"] == "Load"
        assert stages[0]["state"] == "pending"

    def test_start_changes_state(self):
        svc = ProcessingService()
        svc.start()
        assert svc.state == ExecutionState.RUNNING
        assert svc.is_running is True

    def test_start_adds_log(self):
        svc = ProcessingService()
        svc.start()
        assert len(svc.logs) >= 1
        assert svc.logs[0].level == "info"

    def test_start_resets_state(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.3)
        svc.cancel()
        svc.start()
        assert svc.state == ExecutionState.RUNNING

    def test_pause_and_resume(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        svc.pause()
        assert svc.is_paused is True
        svc.resume()
        assert svc.is_paused is False

    def test_cancel(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        svc.cancel()
        assert svc.state == ExecutionState.CANCELLED
        assert svc.is_cancelled is True

    def test_cancel_adds_log(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        l1 = len(svc.logs)
        svc.cancel()
        assert len(svc.logs) > l1

    def test_retry(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        svc.cancel()
        svc.retry()
        assert svc.state == ExecutionState.PENDING

    def test_progress_updates(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(1.0)
        assert svc.progress > 0
        assert svc.rows_processed > 0
        assert svc.elapsed_seconds > 0
        svc.cancel()

    def test_current_stage_label(self):
        svc = ProcessingService()
        assert svc.current_stage_label == "Load"

    def test_logs_generated(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.5)
        assert len(svc.logs) > 0
        svc.cancel()

    def test_metrics_populated(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.5)
        m = svc.metrics
        assert "memory_mb" in m
        assert "cpu_pct" in m
        svc.cancel()

    def test_performance_data(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.3)
        p = svc.performance_data
        assert "memory_trend" in p
        assert "cpu_trend" in p
        svc.cancel()

    def test_results_summary(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.3)
        r = svc.results_summary
        assert "rows_processed" in r
        assert "stores" in r
        assert r["stores"] == 45
        svc.cancel()

    def test_execution_result(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.3)
        r = svc.execution_result
        assert r.state in (ExecutionState.RUNNING,)
        assert len(r.step_results) == 6
        svc.cancel()

    def test_cannot_start_when_running(self):
        svc = ProcessingService()
        svc.start()
        svc.start()  # second start while running
        assert svc.state == ExecutionState.RUNNING

    def test_retry_from_failed(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        svc.cancel()
        svc.retry()
        assert svc.state == ExecutionState.PENDING

    def test_on_change_callback(self):
        svc = ProcessingService()
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.start()
        time.sleep(0.2)
        assert len(calls) >= 1
        svc.cancel()

    def test_multiple_pause_resume(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.1)
        for _ in range(3):
            svc.pause()
            time.sleep(0.05)
            svc.resume()
            time.sleep(0.05)
        assert svc.is_paused is False
        svc.cancel()

    def test_rows_per_sec(self):
        svc = ProcessingService()
        svc.start()
        time.sleep(0.5)
        assert svc.rows_per_sec >= 0
        svc.cancel()


class TestProcessingController:
    def test_start_notifies(self):
        notify = NotificationService()
        svc = ProcessingService()
        ctrl = ProcessingController(svc, notify)
        ctrl.start()
        assert svc.state == ExecutionState.RUNNING
        assert len(notify.notifications) == 1
        svc.cancel()

    def test_start_when_running_shows_warning(self):
        notify = NotificationService()
        svc = ProcessingService()
        ctrl = ProcessingController(svc, notify)
        ctrl.start()
        ctrl.start()  # second start while running
        assert any(n["type_value"] == "warning" for n in notify.notifications)
        svc.cancel()

    def test_pause_resume(self):
        notify = NotificationService()
        svc = ProcessingService()
        ctrl = ProcessingController(svc, notify)
        ctrl.start()
        time.sleep(0.1)
        ctrl.pause()
        assert svc.is_paused is True
        ctrl.resume()
        assert svc.is_paused is False
        svc.cancel()

    def test_cancel(self):
        notify = NotificationService()
        svc = ProcessingService()
        ctrl = ProcessingController(svc, notify)
        ctrl.start()
        time.sleep(0.1)
        ctrl.cancel()
        assert svc.is_cancelled is True

    def test_retry(self):
        notify = NotificationService()
        svc = ProcessingService()
        ctrl = ProcessingController(svc, notify)
        ctrl.start()
        time.sleep(0.1)
        ctrl.cancel()
        ctrl.retry()
        assert svc.state == ExecutionState.PENDING

    def test_properties_delegate(self):
        svc = ProcessingService()
        ctrl = ProcessingController(svc, NotificationService())
        assert ctrl.state == ExecutionState.PENDING
        assert ctrl.is_running is False
        assert ctrl.is_completed is False
        assert ctrl.is_paused is False
        assert ctrl.progress == 0.0
        assert ctrl.current_stage_index == 0
        assert ctrl.current_stage_label == "Load"
        assert ctrl.rows_processed == 0
        assert ctrl.elapsed_seconds == 0.0
        assert ctrl.rows_per_sec == 0.0
        assert len(ctrl.pipeline_stages) == 6
        assert len(ctrl.logs) == 0
        assert "memory_mb" in ctrl.metrics
        assert "memory_trend" in ctrl.performance_data
        assert "rows_processed" in ctrl.results_summary
        assert ctrl.execution_result.state == ExecutionState.PENDING
