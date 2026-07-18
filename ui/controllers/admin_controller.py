"""Admin controller — bridges admin service to UI (Sprint 9)."""

from typing import Any, Dict, List, Optional
from ui.services.admin_service import AdminService
from ui.services.notification_service import NotificationService


class AdminController:
    """Controls Administration Center operations from the UI."""

    def __init__(self, svc: AdminService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    @property
    def system_health(self) -> Dict[str, Any]:
        return self._svc.system_health

    @property
    def project_history(self) -> List[Dict[str, Any]]:
        return self._svc.project_history

    def select_project(self, name: str) -> None:
        self._svc.select_project(name)

    @property
    def selected_project(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_project

    @property
    def execution_history(self) -> List[Dict[str, Any]]:
        return self._svc.execution_history

    def select_execution(self, exec_id: str) -> None:
        self._svc.select_execution(exec_id)

    @property
    def selected_execution(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_execution

    @property
    def all_logs(self) -> List[Dict[str, Any]]:
        return self._svc.all_logs

    @property
    def filtered_logs(self) -> List[Dict[str, Any]]:
        return self._svc.filtered_logs

    @property
    def log_sources(self) -> List[str]:
        return self._svc.log_sources

    def set_log_search(self, query: str) -> None:
        self._svc.set_log_search(query)

    def set_log_severity(self, severity: Optional[str]) -> None:
        self._svc.set_log_severity(severity)

    def set_log_source(self, source: Optional[str]) -> None:
        self._svc.set_log_source(source)

    def select_log(self, index: int) -> None:
        self._svc.select_log(index)

    @property
    def selected_log(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_log

    def export_logs(self) -> str:
        data = self._svc.export_logs()
        self._notify.success("Logs exported")
        return data

    @property
    def diagnostics(self) -> Dict[str, Any]:
        return self._svc.diagnostics

    @property
    def storage(self) -> Dict[str, Any]:
        return self._svc.storage

    @property
    def settings(self) -> Dict[str, Any]:
        return self._svc.settings

    @property
    def default_settings(self) -> Dict[str, Any]:
        return self._svc.default_settings

    def update_setting(self, section: str, key: str, value: Any) -> None:
        self._svc.update_setting(section, key, value)
        self._notify.info(f"Updated {section}.{key}")

    def reset_settings(self) -> None:
        self._svc.reset_settings()
        self._notify.info("Settings reset to defaults")

    @property
    def maintenance_actions(self) -> List[Dict[str, Any]]:
        return self._svc.maintenance_actions

    def run_maintenance(self, action_id: str) -> None:
        result = self._svc.run_maintenance(action_id)
        self._notify.success(result)

    @property
    def about(self) -> Dict[str, Any]:
        return self._svc.about

    @property
    def status_bar(self) -> Dict[str, Any]:
        return self._svc.status_bar
