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

    def __init__(self, persistence=None, context=None):
        self._projects: Dict[str, Dict[str, Any]] = {}
        self._current_project_id: Optional[str] = None
        self._persistence = persistence
        self._context = context

        # Load from persistence if available
        if self._persistence:
            loaded = self._persistence.load_projects()
            for p in loaded:
                pid = p.get("id")
                if pid:
                    self._projects[pid] = p

        # Seed demo projects only if no persisted data
        if not self._projects:
            self._seed_demo_projects()

    def _seed_demo_projects(self) -> None:
        now = datetime.now()
        demos = [
            {
                "name": "Retail Sales Q2",
                "description": "Q2 2026 retail sales data processing pipeline",
                "source": "/data/retail/sales_q2",
                "created": now,
                "modified": now,
            },
            {
                "name": "Inventory Analysis",
                "description": "Warehouse inventory reconciliation and validation",
                "source": "/data/inventory/2026",
                "created": now,
                "modified": now,
            },
            {
                "name": "Customer Feedback",
                "description": "Customer review sentiment and aggregation pipeline",
                "source": "/data/customer/feedback",
                "created": now,
                "modified": now,
            },
        ]
        for p in demos:
            pid = p["name"].lower().replace(" ", "_")
            p["id"] = pid
            self._projects[pid] = p
        self._persist()

    def create_project(self, name: str, description: str = "",
                       source: str = "") -> Dict[str, Any]:
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
