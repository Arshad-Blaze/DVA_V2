"""Requirement controller — bridges requirement service to UI (Sprint 5)."""

from typing import Any, Dict, List, Optional

from ui.services.requirement_service import RequirementService
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import CapabilityMatrix, ExecutionStep, OperationContext


class RequirementController:
    """Controls Analysis Planner operations from the UI."""

    def __init__(self, svc: RequirementService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def select_goal(self, goal_id: str) -> None:
        self._svc.select_goal(goal_id)
        goal = self._svc.selected_goal
        self._notify.info(f"Goal selected: {goal['label'] if goal else goal_id}")

    def clear_goal(self) -> None:
        self._svc.clear_goal()
        self._notify.info("Goal cleared")

    def accept_recommendation(self) -> None:
        self._svc.accept_recommendation()
        self._notify.success("Recommendation accepted")

    def confirm_plan(self) -> None:
        if self._svc.can_confirm:
            self._svc.confirm_plan()
            self._notify.success("Analysis plan confirmed. Ready for execution.")
        else:
            missing_reason = []
            if self._svc.selected_goal_id is None:
                missing_reason.append("No goal selected")
            if not self._svc.recommendation_accepted:
                missing_reason.append("Recommendation not accepted")
            if self._svc.missing_inputs:
                missing_reason.append(f"Missing inputs: {', '.join(m['input'] for m in self._svc.missing_inputs)}")
            self._notify.warning("Cannot confirm: " + "; ".join(missing_reason))

    def reset(self) -> None:
        self._svc.reset()
        self._notify.info("Plan reset")

    @property
    def available_goals(self) -> List[Dict[str, Any]]:
        return self._svc.available_goals

    @property
    def selected_goal_id(self) -> Optional[str]:
        return self._svc.selected_goal_id

    @property
    def selected_goal(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_goal

    @property
    def recommendation(self) -> Dict[str, Any]:
        return self._svc.recommendation

    @property
    def recommendation_accepted(self) -> bool:
        return self._svc.recommendation_accepted

    @property
    def capability_matrix(self) -> CapabilityMatrix:
        return self._svc.capability_matrix

    @property
    def capability_descriptions(self) -> Dict[str, Dict[str, str]]:
        return self._svc.capability_descriptions

    @property
    def execution_plan(self) -> List[ExecutionStep]:
        return self._svc.execution_plan

    @property
    def execution_plan_count(self) -> int:
        return self._svc.execution_plan_count

    @property
    def expected_outputs(self) -> List[str]:
        return self._svc.expected_outputs

    @property
    def execution_estimates(self) -> Dict[str, Any]:
        return self._svc.execution_estimates

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return self._svc.warnings

    @property
    def missing_inputs(self) -> List[Dict[str, str]]:
        return self._svc.missing_inputs

    @property
    def readiness(self) -> Dict[str, bool]:
        return self._svc.readiness

    @property
    def overall_readiness(self) -> str:
        return self._svc.overall_readiness

    @property
    def is_confirmed(self) -> bool:
        return self._svc.is_confirmed

    @property
    def can_confirm(self) -> bool:
        return self._svc.can_confirm

    def get_operation_context(self) -> OperationContext:
        return self._svc.get_operation_context()
