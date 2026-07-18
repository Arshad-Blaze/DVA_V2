"""Persistence service — high-level save/load/backup/restore API.

Sits between services (ProjectService, ConnectionService, etc.)
and the StorageService. Workspaces and Controllers never touch
this directly — they go through their respective Services.
"""

from typing import Any, Dict, List, Optional

from ui.services.storage_service import StorageService
from ui.services.serialization_service import (
    serialize_projects, deserialize_projects,
    serialize_connections, deserialize_connections,
    serialize_context, deserialize_context,
    serialize_preferences, deserialize_preferences,
)
from ui.services.migration_service import MigrationService
from ui.services.workspace_context import WorkspaceContext


class PersistenceService:
    """Application-level persistence API.

    All UI data (projects, connections, session, preferences)
    flows through this service.
    """

    def __init__(self, storage: StorageService,
                 migration: MigrationService,
                 context: WorkspaceContext):
        self._storage = storage
        self._migration = migration
        self._context = context

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def save_projects(self, projects: List[Dict[str, Any]]) -> None:
        data = serialize_projects(projects)
        self._storage.write_json("projects", "all", data)

    def load_projects(self) -> List[Dict[str, Any]]:
        data = self._storage.read_json("projects", "all", default=[])
        return deserialize_projects(data) if isinstance(data, list) else []

    def save_project(self, project: Dict[str, Any]) -> None:
        projects = self.load_projects()
        pid = project.get("id")
        projects = [p for p in projects if p.get("id") != pid]
        projects.append(project)
        self.save_projects(projects)

    def delete_project(self, project_id: str) -> bool:
        projects = self.load_projects()
        before = len(projects)
        projects = [p for p in projects if p.get("id") != project_id]
        if len(projects) == before:
            return False
        self.save_projects(projects)
        return True

    # ------------------------------------------------------------------
    # Connections
    # ------------------------------------------------------------------

    def save_connections(self, connections: List[Dict[str, Any]]) -> None:
        data = serialize_connections(connections)
        self._storage.write_json("connections", "all", data)

    def load_connections(self) -> List[Dict[str, Any]]:
        data = self._storage.read_json("connections", "all", default=[])
        return deserialize_connections(data) if isinstance(data, list) else []

    def save_connection(self, connection: Dict[str, Any]) -> None:
        connections = self.load_connections()
        cid = connection.get("id")
        connections = [c for c in connections if c.get("id") != cid]
        connections.append(connection)
        self.save_connections(connections)

    def delete_connection(self, connection_id: str) -> bool:
        connections = self.load_connections()
        before = len(connections)
        connections = [c for c in connections if c.get("id") != connection_id]
        if len(connections) == before:
            return False
        self.save_connections(connections)
        return True

    # ------------------------------------------------------------------
    # Session
    # ------------------------------------------------------------------

    def save_session(self) -> None:
        data = serialize_context(self._context.to_dict())
        self._storage.write_json("sessions", "last", data)

    def load_session(self) -> Optional[Dict[str, Any]]:
        data = self._storage.read_json("sessions", "last")
        if data is None:
            return None
        return deserialize_context(data)

    def restore_session(self) -> bool:
        """Restore the persisted session into the WorkspaceContext."""
        data = self.load_session()
        if data is None:
            return False
        self._context.from_dict(data)
        return True

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def save_preferences(self, prefs: Dict[str, Any]) -> None:
        data = serialize_preferences(prefs)
        self._storage.write_json("settings", "preferences", data)

    def load_preferences(self) -> Dict[str, Any]:
        data = self._storage.read_json("settings", "preferences", default={})
        return deserialize_preferences(data)

    # ------------------------------------------------------------------
    # Backup / Restore
    # ------------------------------------------------------------------

    def create_backup(self, label: str = "") -> str:
        return self._storage.create_backup(label)

    def list_backups(self) -> List[Dict[str, Any]]:
        return self._storage.list_backups()

    def restore_backup(self, backup_name: str) -> bool:
        return self._storage.restore_backup(backup_name)

    # ------------------------------------------------------------------
    # Migration
    # ------------------------------------------------------------------

    def run_migrations(self) -> None:
        self._migration.run()

    def storage_version(self) -> int:
        return self._migration.current_version()

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def clear_all(self) -> None:
        self._storage.clear_all()
