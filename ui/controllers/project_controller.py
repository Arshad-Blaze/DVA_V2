"""Project controller — bridges project service to UI."""

from typing import Any, Callable, Dict, List, Optional

from ui.services.project_service import ProjectService
from ui.services.notification_service import NotificationService


class ProjectController:
    """Controls project CRUD operations from the UI."""

    def __init__(self, project_svc: ProjectService, notify_svc: NotificationService):
        self._project_svc = project_svc
        self._notify_svc = notify_svc
        self._on_change: Optional[Callable] = None

    def create_project(self, name: str, description: str = "",
                       source: str = "") -> Optional[Dict[str, Any]]:
        if not name or not name.strip():
            self._notify_svc.warning("Project name is required")
            return None
        project = self._project_svc.create_project(name.strip(), description.strip(), source.strip())
        self._notify_svc.success(f"Project '{name}' created")
        if self._on_change:
            self._on_change()
        return project

    def open_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self._project_svc.open_project(project_id)
        if project:
            self._notify_svc.info(f"Opened project '{project['name']}'")
            if self._on_change:
                self._on_change()
        else:
            self._notify_svc.error("Project not found")
        return project

    def rename_project(self, project_id: str, new_name: str) -> bool:
        if not new_name or not new_name.strip():
            self._notify_svc.warning("Project name is required")
            return False
        result = self._project_svc.rename_project(project_id, new_name.strip())
        if result:
            self._notify_svc.success(f"Project renamed to '{new_name}'")
            if self._on_change:
                self._on_change()
        else:
            self._notify_svc.error("Project not found")
        return result

    def delete_project(self, project_id: str) -> bool:
        project = self._project_svc.get_project(project_id)
        if project and self._project_svc.delete_project(project_id):
            self._notify_svc.success(f"Project '{project['name']}' deleted")
            if self._on_change:
                self._on_change()
            return True
        self._notify_svc.error("Project not found")
        return False

    def close_project(self) -> None:
        self._project_svc.close_project()
        self._notify_svc.info("Project closed")
        if self._on_change:
            self._on_change()

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    @property
    def current_project(self) -> Optional[Dict[str, Any]]:
        return self._project_svc.current_project

    @property
    def projects(self) -> List[Dict[str, Any]]:
        return self._project_svc.list_projects()

    @property
    def recent_projects(self) -> List[Dict[str, Any]]:
        return self._project_svc.recent_projects()
