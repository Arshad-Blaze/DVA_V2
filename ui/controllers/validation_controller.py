"""Validation controller — bridges validation service to UI (Sprint 7)."""

from typing import Any, Dict, List, Optional
from ui.services.validation_service import ValidationService
from ui.services.notification_service import NotificationService


class ValidationController:
    """Controls Validation Center operations from the UI."""

    def __init__(self, svc: ValidationService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def approve(self) -> None:
        self._svc.approve()
        self._notify.success("Dataset approved. Ready for reports.")

    def reject(self) -> None:
        self._svc.reject()
        self._notify.warning("Dataset rejected — review required")

    def reset(self) -> None:
        self._svc.reset()
        self._notify.info("Approval reset")

    def export_report(self) -> str:
        data = self._svc.export_report()
        self._notify.success("Validation report exported")
        return data

    def export_failed(self) -> str:
        data = self._svc.export_failed_records()
        self._notify.success("Failed records exported")
        return data

    def set_severity_filter(self, severity: str) -> None:
        self._svc.set_severity_filter(severity)

    def set_search_query(self, query: str) -> None:
        self._svc.set_search_query(query)

    def select_issue(self, index: int) -> None:
        self._svc.select_issue(index)

    def select_rule(self, rule_name: str) -> None:
        self._svc.select_rule(rule_name)

    @property
    def dashboard(self) -> Dict[str, Any]:
        return self._svc.dashboard

    @property
    def heat_map_rows(self) -> List[str]:
        return self._svc.heat_map_rows

    @property
    def heat_map_columns(self) -> List[str]:
        return self._svc.heat_map_columns

    @property
    def heat_map_data(self) -> Dict[str, Dict[str, str]]:
        return self._svc.heat_map_data

    @property
    def all_issues(self) -> List[Dict[str, Any]]:
        return self._svc.all_issues

    @property
    def filtered_issues(self) -> List[Dict[str, Any]]:
        return self._svc.filtered_issues

    @property
    def issue_count(self) -> int:
        return self._svc.issue_count

    @property
    def selected_issue(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_issue

    @property
    def comparison_data(self) -> List[Dict[str, Any]]:
        return self._svc.comparison_data

    @property
    def all_rules(self) -> List[Dict[str, Any]]:
        return self._svc.all_rules

    @property
    def selected_rule(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_rule

    @property
    def business_impact(self) -> Dict[str, Any]:
        return self._svc.business_impact

    @property
    def suggested_actions(self) -> List[Dict[str, Any]]:
        return self._svc.suggested_actions

    @property
    def timeline_stages(self) -> List[Dict[str, Any]]:
        return self._svc.timeline_stages

    @property
    def is_approved(self) -> bool:
        return self._svc.is_approved

    @property
    def is_rejected(self) -> bool:
        return self._svc.is_rejected
