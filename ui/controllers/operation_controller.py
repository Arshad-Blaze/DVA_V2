"""Operation controller — bridges operation service to UI (Sprint 6A)."""

from typing import Any, Dict, List

from ui.services.operation_service import OperationService
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import ExecutionStep


class OperationController:
    """Controls Execution Planner operations from the UI."""

    def __init__(self, svc: OperationService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def update_config(self, key: str, value: Any) -> None:
        self._svc.set_config(key, value)
        self._notify.info(f"Config updated: {key} = {value}")

    def reset_config(self) -> None:
        self._svc.reset_config()
        self._notify.info("Configuration reset to defaults")

    def approve(self) -> None:
        if self._svc.can_approve:
            self._svc.approve()
            self._notify.success("Execution plan approved. Ready for processing.")
        else:
            self._notify.warning("Cannot approve: readiness checklist incomplete")

    def reject(self) -> None:
        self._svc.reject()
        self._notify.info("Execution plan rejected")

    @property
    def pipeline_stages(self) -> List[Dict[str, Any]]:
        return self._svc.pipeline_stages

    @property
    def execution_steps(self) -> List[ExecutionStep]:
        return self._svc.execution_steps

    @property
    def execution_summary(self) -> Dict[str, Any]:
        return self._svc.execution_summary

    @property
    def config(self) -> Dict[str, Any]:
        return self._svc.config

    @property
    def resource_estimates(self) -> Dict[str, Any]:
        return self._svc.resource_estimates

    @property
    def expected_outputs(self) -> List[str]:
        return self._svc.expected_outputs

    @property
    def readiness_items(self) -> List[Dict[str, Any]]:
        return self._svc.readiness_items

    @property
    def overall_readiness(self) -> str:
        return self._svc.overall_readiness

    @property
    def is_approved(self) -> bool:
        return self._svc.is_approved

    @property
    def can_approve(self) -> bool:
        return self._svc.can_approve
