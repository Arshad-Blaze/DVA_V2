"""UI Tests — Detection Service & Controller (Sprint 3)."""

import pytest
from ui.services.detection_service import DetectionService
from ui.controllers.detection_controller import DetectionController
from ui.services.notification_service import NotificationService


class TestDetectionService:
    def test_default_state(self):
        svc = DetectionService()
        assert svc.result is not None
        assert svc.detection_status == "idle"
        assert svc.is_accepted is False
        assert svc.has_overrides is False
        assert svc.selected_file == "sales_q2_2026.csv"

    def test_timeline_has_steps(self):
        svc = DetectionService()
        assert len(svc.timeline) == 7
        assert svc.timeline[0]["step"] == "File Loaded"
        assert svc.timeline[-1]["step"] == "Detection Complete"

    def test_warnings(self):
        svc = DetectionService()
        assert len(svc.warnings) == 3
        assert svc.warnings[0]["type"] == "info"

    def test_result_fields(self):
        svc = DetectionService()
        r = svc.result
        assert r.file_type.value == "delimited"
        assert r.delimiter == ","
        assert r.encoding == "utf-8"
        assert r.has_header is True
        assert len(r.columns) == 9
        assert r.confidence == 0.95

    def test_run_detection(self):
        svc = DetectionService()
        svc.run_detection()
        assert svc.detection_status == "completed"

    def test_accept_detection(self):
        svc = DetectionService()
        svc.accept_detection()
        assert svc.is_accepted is True
        assert svc.detection_status == "accepted"

    def test_validate_detection(self):
        svc = DetectionService()
        assert svc.validate_detection() is True

    def test_set_override(self):
        svc = DetectionService()
        svc.set_override("delimiter", "|")
        assert svc.has_overrides is True
        assert svc.get_override("delimiter") == "|"
        assert svc.is_accepted is False  # overrides reset acceptance

    def test_clear_override(self):
        svc = DetectionService()
        svc.set_override("delimiter", "|")
        svc.clear_override("delimiter")
        assert svc.has_overrides is False

    def test_clear_all_overrides(self):
        svc = DetectionService()
        svc.set_override("a", 1)
        svc.set_override("b", 2)
        svc.clear_all_overrides()
        assert svc.has_overrides is False

    def test_effective_value_without_override(self):
        svc = DetectionService()
        result = svc.get_effective_value("delimiter", ",")
        assert result == ","

    def test_effective_value_with_override(self):
        svc = DetectionService()
        svc.set_override("delimiter", "|")
        result = svc.get_effective_value("delimiter", ",")
        assert result == "|"

    def test_switch_file(self):
        svc = DetectionService()
        svc.switch_file("other.csv")
        assert svc.selected_file == "other.csv"

    def test_selected_files(self):
        svc = DetectionService()
        files = svc.selected_files
        assert len(files) == 3
        assert "sales_q2_2026.csv" in files

    def test_detection_summary(self):
        svc = DetectionService()
        summary = svc.get_detection_summary()
        assert summary["file_type"] == "delimited"
        assert summary["delimiter"] == ","
        assert summary["confidence"] == 0.95
        assert summary["columns"] == 9

    def test_on_change_callback(self):
        svc = DetectionService()
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.run_detection()
        assert len(calls) >= 1

    def test_connection_id(self):
        svc = DetectionService()
        assert svc.connection_id == "production_data"


class TestDetectionController:
    def test_run_detection_notifies(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        ctrl.run_detection()
        assert len(notify.notifications) == 1

    def test_accept_notifies(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        ctrl.accept_detection()
        assert svc.is_accepted is True
        assert len(notify.notifications) == 1

    def test_validate_detection(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        assert ctrl.validate_detection() is True

    def test_set_override(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        ctrl.set_override("delimiter", ";")
        assert svc.get_override("delimiter") == ";"

    def test_switch_file(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        ctrl.switch_file("new_file.csv")
        assert svc.selected_file == "new_file.csv"

    def test_get_summary(self):
        notify = NotificationService()
        svc = DetectionService()
        ctrl = DetectionController(svc, notify)
        summary = ctrl.get_summary()
        assert summary["file_type"] == "delimited"
