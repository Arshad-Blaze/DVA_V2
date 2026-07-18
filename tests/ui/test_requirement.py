"""UI Tests — Analysis Planner (Sprint 5)."""

import pytest
from ui.services.requirement_service import RequirementService
from ui.controllers.requirement_controller import RequirementController
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import CapabilityMatrix, ProcessingMode, BusinessGoal


class TestRequirementService:
    def test_default_state(self):
        svc = RequirementService()
        assert svc.selected_goal_id is None
        assert svc.is_confirmed is False
        assert svc.recommendation_accepted is False

    def test_available_goals(self):
        svc = RequirementService()
        goals = svc.available_goals
        assert len(goals) == 9
        assert goals[0]["id"] == "retailer_onboarding"

    def test_select_goal(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        assert svc.selected_goal_id == "aggregate_calculate"
        assert svc.is_confirmed is False

    def test_select_goal_invalid(self):
        svc = RequirementService()
        svc.select_goal("nonexistent")
        assert svc.selected_goal_id is None

    def test_clear_goal(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.clear_goal()
        assert svc.selected_goal_id is None

    def test_selected_goal_property(self):
        svc = RequirementService()
        svc.select_goal("store_validation")
        g = svc.selected_goal
        assert g is not None
        assert g["id"] == "store_validation"
        assert g["label"] == "Store Validation"

    def test_recommendation_before_selection(self):
        svc = RequirementService()
        r = svc.recommendation
        assert "workflow" in r
        assert r["confidence"] > 0

    def test_recommendation_after_selection(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        r = svc.recommendation
        assert "aggregate" in r["workflow"].lower()
        assert r["confidence"] == 0.95

    def test_accept_recommendation(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        assert svc.recommendation_accepted is False
        svc.accept_recommendation()
        assert svc.recommendation_accepted is True

    def test_capability_matrix_default(self):
        svc = RequirementService()
        m = svc.capability_matrix
        assert m.can_aggregate is False
        assert m.can_calculate is False

    def test_capability_matrix_after_selection(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        m = svc.capability_matrix
        assert m.can_aggregate is True
        assert m.can_calculate is True
        assert m.can_validate is True
        assert m.can_compare is False

    def test_capability_descriptions(self):
        svc = RequirementService()
        d = svc.capability_descriptions
        assert "can_aggregate" in d
        assert d["can_aggregate"]["label"] == "Aggregation"

    def test_execution_plan_default(self):
        svc = RequirementService()
        plan = svc.execution_plan
        assert len(plan) == 5

    def test_execution_plan_after_selection(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        plan = svc.execution_plan
        assert len(plan) == 6
        assert plan[0].action == "Load Data"
        assert plan[1].action == "Aggregate"
        assert plan[-1].action == "Export"

    def test_expected_outputs_default(self):
        svc = RequirementService()
        outs = svc.expected_outputs
        assert len(outs) == 2

    def test_expected_outputs_after_selection(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        outs = svc.expected_outputs
        assert "Store Summary Report (Excel)" in outs
        assert "Item Summary Report (Excel)" in outs

    def test_execution_estimates_default(self):
        svc = RequirementService()
        e = svc.execution_estimates
        assert e["runtime"] == "1-2 min"

    def test_execution_estimates_after_selection(self):
        svc = RequirementService()
        svc.select_goal("retailer_onboarding")
        e = svc.execution_estimates
        assert e["runtime"] == "5-10 min"
        assert e["complexity"] == "High"

    def test_warnings_default(self):
        svc = RequirementService()
        w = svc.warnings
        assert len(w) == 0

    def test_warnings_for_migration(self):
        svc = RequirementService()
        svc.select_goal("migration_validation")
        w = svc.warnings
        assert len(w) == 1
        assert w[0]["severity"] == "error"

    def test_missing_inputs_default(self):
        svc = RequirementService()
        m = svc.missing_inputs
        assert len(m) == 0

    def test_missing_inputs_for_migration(self):
        svc = RequirementService()
        svc.select_goal("migration_validation")
        m = svc.missing_inputs
        assert len(m) == 1
        assert m[0]["input"] == "Reference Dataset"

    def test_readiness_default(self):
        svc = RequirementService()
        r = svc.readiness
        assert r["project_ready"] is True
        assert r["requirement_complete"] is False

    def test_readiness_after_confirm(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        svc.confirm_plan()
        r = svc.readiness
        assert r["requirement_complete"] is True

    def test_overall_readiness_initial(self):
        svc = RequirementService()
        assert svc.overall_readiness == "Almost Ready"  # all prereqs met, requirement not complete

    def test_overall_readiness_after_confirm(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        svc.confirm_plan()
        assert svc.overall_readiness == "Ready"

    def test_can_confirm_before_selection(self):
        svc = RequirementService()
        assert svc.can_confirm is False

    def test_can_confirm_after_selection(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        assert svc.can_confirm is False  # need to accept recommendation

    def test_can_confirm_after_acceptance(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        assert svc.can_confirm is True

    def test_can_confirm_blocked_by_missing_inputs(self):
        svc = RequirementService()
        svc.select_goal("migration_validation")
        svc.accept_recommendation()
        assert svc.can_confirm is False  # missing inputs

    def test_confirm_plan(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        svc.confirm_plan()
        assert svc.is_confirmed is True

    def test_confirm_plan_blocked(self):
        svc = RequirementService()
        svc.confirm_plan()  # no goal selected, no recommendation
        assert svc.is_confirmed is False

    def test_reset(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        svc.confirm_plan()
        svc.reset()
        assert svc.selected_goal_id is None
        assert svc.is_confirmed is False
        assert svc.recommendation_accepted is False

    def test_operation_context(self):
        svc = RequirementService()
        svc.select_goal("aggregate_calculate")
        svc.accept_recommendation()
        ctx = svc.get_operation_context()
        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
        assert ctx.business_goal == BusinessGoal.CALCULATION
        assert ctx.recommended_workflow != ""
        assert len(ctx.execution_plan) == 6
        assert len(ctx.expected_outputs) > 0

    def test_on_change_callback(self):
        svc = RequirementService()
        calls = []
        svc.on_change(lambda: calls.append(1))
        svc.select_goal("aggregate_calculate")
        assert len(calls) >= 1


class TestRequirementController:
    def test_select_goal_notifies(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        assert svc.selected_goal_id == "aggregate_calculate"
        assert len(notify.notifications) == 1

    def test_clear_goal(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        ctrl.clear_goal()
        assert svc.selected_goal_id is None

    def test_accept_recommendation(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        ctrl.accept_recommendation()
        assert svc.recommendation_accepted is True

    def test_confirm_plan(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        ctrl.accept_recommendation()
        ctrl.confirm_plan()
        assert svc.is_confirmed is True
        assert notify.notifications[-1]["type_value"] == "success"

    def test_confirm_blocked_notifies_warning(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.confirm_plan()  # no goal selected
        assert svc.is_confirmed is False
        assert notify.notifications[0]["type_value"] == "warning"

    def test_reset(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        ctrl.accept_recommendation()
        ctrl.confirm_plan()
        ctrl.reset()
        assert svc.selected_goal_id is None
        assert svc.is_confirmed is False

    def test_properties_delegate(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        assert len(ctrl.available_goals) == 9
        assert ctrl.selected_goal_id is None
        assert ctrl.recommendation_accepted is False
        assert isinstance(ctrl.capability_matrix, CapabilityMatrix)
        assert len(ctrl.capability_descriptions) == 7
        assert len(ctrl.execution_plan) == 5
        assert ctrl.execution_plan_count == 5
        assert len(ctrl.expected_outputs) > 0
        assert ctrl.execution_estimates["runtime"] == "1-2 min"
        assert len(ctrl.missing_inputs) == 0
        assert ctrl.overall_readiness in ("Ready", "Review Required", "Almost Ready")
        assert ctrl.is_confirmed is False
        assert ctrl.can_confirm is False

    def test_select_goal_updates_selected_goal(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("store_validation")
        g = ctrl.selected_goal
        assert g["label"] == "Store Validation"
        assert g["id"] == "store_validation"

    def test_warnings_delegate(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("migration_validation")
        assert len(ctrl.warnings) == 1

    def test_readiness(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        r = ctrl.readiness
        assert r["project_ready"] is True
        assert r["preview_approved"] is True

    def test_operation_context(self):
        notify = NotificationService()
        svc = RequirementService()
        ctrl = RequirementController(svc, notify)
        ctrl.select_goal("aggregate_calculate")
        ctrl.accept_recommendation()
        ctx = ctrl.get_operation_context()
        assert ctx.mode == ProcessingMode.AGGREGATE_AND_CALCULATE
