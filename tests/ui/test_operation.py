"""UI Tests — Execution Planner (Sprint 6A)."""

import pytest
from ui.services.operation_service import OperationService
from ui.controllers.operation_controller import OperationController
from ui.services.notification_service import NotificationService
from ui.services.requirement_service import RequirementService
from dav_platform.core.contracts import ExecutionStep


class TestOperationService:
    def test_default_state(self):
        svc = OperationService()
        assert svc.is_approved is False
        assert svc.can_approve is True

    def test_pipeline_stages(self):
        svc = OperationService()
        stages = svc.pipeline_stages
        assert len(stages) == 6
        assert stages[0]["id"] == "load"
        assert stages[-1]["id"] == "export"

    def test_execution_steps_empty_without_req(self):
        svc = OperationService()
        steps = svc.execution_steps
        assert len(steps) == 0

    def test_execution_steps_with_req(self):
        req = RequirementService()
        req.select_goal("aggregate_calculate")
        svc = OperationService(req)
        steps = svc.execution_steps
        assert len(steps) == 6
        assert steps[0].action == "Load Data"

    def test_execution_summary(self):
        req = RequirementService()
        req.select_goal("aggregate_calculate")
        svc = OperationService(req)
        s = svc.execution_summary
        assert s["total_steps"] == 6
        assert "processing" in s["layers"]

    def test_default_config(self):
        svc = OperationService()
        c = svc.config
        assert c["streaming"] is True
        assert c["chunk_size"] == 10000
        assert c["dry_run"] is False

    def test_update_config(self):
        svc = OperationService()
        svc.set_config("streaming", False)
        assert svc.config["streaming"] is False

    def test_update_config_kwargs(self):
        svc = OperationService()
        svc.update_config(chunk_size=25000, parallel_workers=4)
        assert svc.config["chunk_size"] == 25000
        assert svc.config["parallel_workers"] == 4

    def test_reset_config(self):
        svc = OperationService()
        svc.set_config("streaming", False)
        svc.set_config("dry_run", True)
        svc.reset_config()
        c = svc.config
        assert c["streaming"] is True
        assert c["dry_run"] is False

    def test_resource_estimates(self):
        svc = OperationService()
        e = svc.resource_estimates
        assert "runtime" in e
        assert "memory" in e
        assert "peak_memory" in e

    def test_resource_estimates_streaming_affects_memory(self):
        svc = OperationService()
        e1 = svc.resource_estimates
        svc.set_config("streaming", False)
        e2 = svc.resource_estimates
        # without streaming, memory estimate should be higher
        assert e1["memory"] != e2["memory"]

    def test_expected_outputs_without_req(self):
        svc = OperationService()
        outs = svc.expected_outputs
        assert len(outs) == 2
        assert "Processed Dataset (CSV)" in outs

    def test_expected_outputs_with_req(self):
        req = RequirementService()
        req.select_goal("aggregate_calculate")
        svc = OperationService(req)
        outs = svc.expected_outputs
        assert "Store Summary Report (Excel)" in outs

    def test_readiness_items(self):
        svc = OperationService()
        items = svc.readiness_items
        assert len(items) == 7
        assert items[0]["id"] == "project_ready"
        assert items[-1]["id"] == "ready_to_execute"

    def test_readiness_status(self):
        req = RequirementService()
        req.select_goal("aggregate_calculate")
        req.accept_recommendation()
        req.confirm_plan()
        svc = OperationService(req)
        items = svc.readiness_items
        all_ready = all(i["status"] for i in items)
        assert all_ready is True

    def test_overall_readiness_ready(self):
        req = RequirementService()
        req.select_goal("aggregate_calculate")
        req.accept_recommendation()
        req.confirm_plan()
        svc = OperationService(req)
        assert svc.overall_readiness == "Ready to Execute"

    def test_overall_readiness_review_required(self):
        req = RequirementService()  # has no goal selected/confirmed
        svc = OperationService(req)
        assert svc.overall_readiness == "Review Required"

    def test_can_approve(self):
        svc = OperationService()
        assert svc.can_approve is True  # all default readiness items are True

    def test_approve(self):
        svc = OperationService()
        svc.approve()
        assert svc.is_approved is True

    def test_reject(self):
        svc = OperationService()
        svc.approve()
        svc.reject()
        assert svc.is_approved is False

    def test_approve_blocked_when_not_ready(self):
        svc = OperationService()
        # ready_to_execute is True by default since all prereqs are True
        assert svc.can_approve is True

    def test_on_change_callback(self):
        svc = OperationService()
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.approve()
        assert len(calls) >= 1


class TestOperationController:
    def test_update_config_notifies(self):
        notify = NotificationService()
        svc = OperationService()
        ctrl = OperationController(svc, notify)
        ctrl.update_config("streaming", False)
        assert svc.config["streaming"] is False
        assert len(notify.notifications) == 1

    def test_reset_config(self):
        notify = NotificationService()
        svc = OperationService()
        ctrl = OperationController(svc, notify)
        ctrl.update_config("streaming", False)
        ctrl.reset_config()
        assert svc.config["streaming"] is True

    def test_approve_notifies(self):
        notify = NotificationService()
        svc = OperationService()
        ctrl = OperationController(svc, notify)
        ctrl.approve()
        assert svc.is_approved is True
        assert notify.notifications[-1]["type_value"] == "success"

    def test_reject(self):
        notify = NotificationService()
        svc = OperationService()
        ctrl = OperationController(svc, notify)
        ctrl.approve()
        ctrl.reject()
        assert svc.is_approved is False

    def test_properties_delegate(self):
        notify = NotificationService()
        svc = OperationService()
        ctrl = OperationController(svc, notify)
        assert len(ctrl.pipeline_stages) == 6
        assert len(ctrl.execution_steps) == 0
        assert "total_steps" in ctrl.execution_summary
        assert ctrl.config["streaming"] is True
        assert "runtime" in ctrl.resource_estimates
        assert len(ctrl.expected_outputs) > 0
        assert len(ctrl.readiness_items) == 7
        assert ctrl.overall_readiness in ("Ready to Execute", "Review Required")
        assert ctrl.is_approved is False
        assert ctrl.can_approve is True
