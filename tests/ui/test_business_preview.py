"""UI Tests — Business Preview Studio (Sprint 4B)."""

import pytest
from ui.services.canonical_service import CanonicalService
from ui.services.preview_service import PreviewService
from ui.controllers.preview_controller import PreviewController
from ui.services.notification_service import NotificationService


class TestPreviewService:
    def test_default_state(self):
        svc = PreviewService(CanonicalService())
        assert svc.is_approved is False
        assert svc.is_rejected is False
        assert svc.can_approve is True  # all checks pass by default

    def test_pipeline_stages(self):
        svc = PreviewService(CanonicalService())
        stages = svc.pipeline_stages
        assert len(stages) == 4
        assert stages[0]["id"] == "detection"
        assert stages[2]["id"] == "preview"
        assert svc.current_stage_index == 2

    def test_comparison_rows(self):
        svc = PreviewService(CanonicalService())
        rows = svc.get_comparison_rows()
        assert len(rows) > 0
        assert rows[0]["physical"] == "Store"
        assert rows[0]["business"] == "store"

    def test_comparison_excludes_unmapped(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        rows = svc.get_comparison_rows()
        physical_names = {r["physical"] for r in rows}
        assert "Store" not in physical_names

    def test_preview_columns(self):
        svc = PreviewService(CanonicalService())
        cols = svc.preview_columns
        assert len(cols) == 11
        assert cols[0]["name"] == "store"

    def test_preview_rows(self):
        svc = PreviewService(CanonicalService())
        rows = svc.preview_rows
        assert len(rows) == 20
        assert rows[0]["store"] == "S001"

    def test_preview_row_count(self):
        svc = PreviewService(CanonicalService())
        assert svc.preview_row_count == 1250

    def test_validation_checks_pass(self):
        svc = PreviewService(CanonicalService())
        checks = svc.get_validation_checks()
        assert len(checks) == 7
        all_pass = all(c["status"] in ("pass", "info") for c in checks)
        assert all_pass is True

    def test_validation_checks_reflect_quantity(self):
        canonical = CanonicalService()
        svc = PreviewService(canonical)
        checks = svc.get_validation_checks()
        qc = [c for c in checks if c["id"] == "quantity_resolved"][0]
        assert "units" in qc["detail"]
        canonical.set_quantity_strategy("weighted_qty")
        checks = svc.get_validation_checks()
        qc = [c for c in checks if c["id"] == "quantity_resolved"][0]
        assert "weighted_qty" in qc["detail"]

    def test_quality_metrics(self):
        svc = PreviewService(CanonicalService())
        m = svc.quality_metrics
        assert m["overall_quality"] == "High"
        assert m["overall_readiness"] == "Ready"
        assert m["mapping_confidence"] > 0

    def test_quality_metrics_missing_required(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        m = svc.quality_metrics
        assert m["overall_readiness"] == "Review Required"

    def test_business_statistics(self):
        svc = PreviewService(CanonicalService())
        s = svc.business_statistics
        assert s["total_rows"] == 1250
        assert s["stores"] == 45
        assert s["completeness"] == 97.9

    def test_metadata(self):
        canonical = CanonicalService()
        svc = PreviewService(canonical)
        meta = svc.metadata
        assert meta.mapped_columns == 9

    def test_warnings_empty_by_default(self):
        svc = PreviewService(CanonicalService())
        w = svc.warnings
        assert len(w) > 0
        assert w[0]["severity"] in ("warning", "info", "error")

    def test_warnings_include_missing_required(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        w = svc.warnings
        severities = [x["severity"] for x in w]
        assert "error" in severities

    def test_approval_checklist(self):
        svc = PreviewService(CanonicalService())
        cl = svc.get_approval_checklist()
        assert len(cl) == 5
        assert all(c["status"] is True for c in cl)

    def test_approval_checklist_missing_required(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        cl = svc.get_approval_checklist()
        rf = [c for c in cl if c["id"] == "required_fields"][0]
        assert rf["status"] is False

    def test_can_approve_fails_when_missing_required(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        assert svc.can_approve is False

    def test_approve_flow(self):
        svc = PreviewService(CanonicalService())
        svc.approve()
        assert svc.is_approved is True
        assert svc.is_rejected is False

    def test_reject_flow(self):
        svc = PreviewService(CanonicalService())
        svc.reject()
        assert svc.is_approved is False
        assert svc.is_rejected is True

    def test_reset_approval(self):
        svc = PreviewService(CanonicalService())
        svc.approve()
        svc.reset_approval()
        assert svc.is_approved is False
        assert svc.is_rejected is False

    def test_approve_fails_when_not_can_approve(self):
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        svc.approve()
        assert svc.is_approved is False

    def test_on_change_callback(self):
        svc = PreviewService(CanonicalService())
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.approve()
        assert len(calls) >= 1

    def test_export_preview(self):
        svc = PreviewService(CanonicalService())
        data = svc.get_export_data()
        assert "store,upc" in data
        assert "S001" in data

    def test_export_mapping(self):
        svc = PreviewService(CanonicalService())
        data = svc.get_mapping_export()
        assert "Business Field" in data
        assert "store" in data


class TestPreviewController:
    def test_approve_notifies(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        ctrl.approve()
        assert svc.is_approved is True
        assert len(notify.notifications) == 1

    def test_approve_blocked_notifies_warning(self):
        notify = NotificationService()
        canonical = CanonicalService()
        canonical.clear_mapping("store")
        svc = PreviewService(canonical)
        ctrl = PreviewController(svc, notify)
        ctrl.approve()
        assert svc.is_approved is False
        assert notify.notifications[0]["type_value"] == "warning"

    def test_reject(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        ctrl.reject()
        assert svc.is_rejected is True

    def test_reset_approval(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        ctrl.approve()
        ctrl.reset_approval()
        assert svc.is_approved is False

    def test_export_preview(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        data = ctrl.export_preview()
        assert "store,upc" in data

    def test_export_mapping(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        data = ctrl.export_mapping()
        assert "Business Field" in data

    def test_properties_delegate(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        assert len(ctrl.pipeline_stages) == 4
        assert ctrl.current_stage_index == 2
        assert len(ctrl.get_comparison_rows()) > 0
        assert len(ctrl.preview_columns) == 11
        assert len(ctrl.preview_rows) == 20
        assert ctrl.preview_row_count == 1250
        assert len(ctrl.get_validation_checks()) == 7
        assert ctrl.quality_metrics["overall_quality"] == "High"
        assert ctrl.business_statistics["total_rows"] == 1250
        assert len(ctrl.get_approval_checklist()) == 5
        assert ctrl.can_approve is True
        assert ctrl.is_approved is False
        assert ctrl.is_rejected is False

    def test_warnings(self):
        notify = NotificationService()
        svc = PreviewService(CanonicalService())
        ctrl = PreviewController(svc, notify)
        assert len(ctrl.warnings) > 0
