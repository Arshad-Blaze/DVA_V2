"""Project service — manages project metadata (no backend coupling).

Supports persistence via optional PersistenceService injection.
If no persistence is provided, operates in-memory (backward compatible).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class ProjectService:
    """Manages project CRUD and state within the UI session.

    When a PersistenceService is provided, all CRUD operations
    automatically persist to disk. Never touches backend.
    """

    def __init__(self, persistence=None, context=None, demo_svc=None):
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._current_project_id: Optional[str] = None
        self._persistence = persistence
        self._context = context
        self._demo_svc = demo_svc

        # Load from persistence if available
        if self._persistence:
            loaded = self._persistence.load_projects()
            for p in loaded:
                pid = p.get("id")
                if pid:
                    self._projects[pid] = p
        # Sync current_project_id from context (restored session)
        if self._context and self._context.current_project_id:
            self._current_project_id = self._context.current_project_id

    def _demo_active(self) -> bool:
        return self._demo_svc is not None and self._demo_svc.is_active

    def create_project(self, name: str, description: str = "",
                       source: str = "") -> Dict[str, Any]:
        if self._demo_active() and "demo" not in name.lower():
            raise PermissionError("Cannot create projects while demo mode is active")
        pid = name.lower().replace(" ", "_")
        now = datetime.now()
        project = {
            "id": pid,
            "name": name,
            "description": description,
            "source": source,
            "created": now,
            "modified": now,
        }
        self._projects[pid] = project
        self._current_project_id = pid
        if self._context:
            self._context.current_project_id = pid
            self._context.add_recent_project(pid)
        self._persist()
        return project

    def open_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        project = self._projects.get(project_id)
        if project:
            self._current_project_id = project_id
            if self._context:
                self._context.current_project_id = project_id
                self._context.add_recent_project(project_id)
        return project

    def rename_project(self, project_id: str, new_name: str) -> bool:
        project = self._projects.get(project_id)
        if not project:
            return False
        new_id = new_name.lower().replace(" ", "_")
        project["name"] = new_name
        project["id"] = new_id
        project["modified"] = datetime.now()
        self._projects[new_id] = project
        if project_id != new_id:
            del self._projects[project_id]
        if self._current_project_id == project_id:
            self._current_project_id = new_id
            if self._context:
                self._context.current_project_id = new_id
        self._persist()
        return True

    def delete_project(self, project_id: str) -> bool:
        if self._demo_active() and not self._demo_svc.is_demo_project(project_id):
            raise PermissionError("Cannot delete projects while demo mode is active")
        if project_id in self._projects:
            del self._projects[project_id]
            if self._current_project_id == project_id:
                self._current_project_id = None
                if self._context:
                    self._context.current_project_id = None
            self._persist()
            return True
        return False

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        return self._projects.get(project_id)

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = list(self._projects.values())
        projects.sort(key=lambda p: p["modified"], reverse=True)
        return projects

    def recent_projects(self, limit: int = 5) -> List[Dict[str, Any]]:
        projects = self.list_projects()
        return projects[:limit]

    @property
    def current_project_id(self) -> Optional[str]:
        return self._current_project_id

    @property
    def current_project(self) -> Optional[Dict[str, Any]]:
        if self._current_project_id:
            return self._projects.get(self._current_project_id)
        return None

    @current_project_id.setter
    def current_project_id(self, value: Optional[str]) -> None:
        self._current_project_id = value
        if self._context:
            self._context.current_project_id = value

    def close_project(self) -> None:
        self._current_project_id = None
        if self._context:
            self._context.current_project_id = None

    def _persist(self) -> None:
        if self._persistence:
            self._persistence.save_projects(self.list_projects())
