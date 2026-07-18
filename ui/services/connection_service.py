"""Connection service — manages data source connections.

Handles connection state, file browsing, and data source configuration.
Never performs actual business logic — only UI state and path browsing.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ConnectionType:
    LOCAL = "local"
    NETWORK = "network"
    DATABASE = "database"
    CLOUD = "cloud"


CONNECTION_TYPES = {
    ConnectionType.LOCAL: {"label": "Local Filesystem", "icon": "folder", "color": "primary"},
    ConnectionType.NETWORK: {"label": "Network Share", "icon": "lan", "color": "info"},
    ConnectionType.DATABASE: {"label": "Database", "icon": "storage", "color": "warning"},
    ConnectionType.CLOUD: {"label": "Cloud Storage", "icon": "cloud", "color": "positive"},
}


class ConnectionService:
    """Manages connection state and file browsing within the UI session."""

    def __init__(self):
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._current_connection_id: Optional[str] = None
        self._current_path: str = "/"

        # Seed demo connections
        self._seed_demo_connections()

    def _seed_demo_connections(self) -> None:
        demos = [
            {
                "name": "Production Data",
                "conn_type": ConnectionType.LOCAL,
                "path": "/data/production",
                "description": "Production data lake connection",
            },
            {
                "name": "Staging Files",
                "conn_type": ConnectionType.LOCAL,
                "path": "/data/staging",
                "description": "Staging area for incoming files",
            },
            {
                "name": "Archive Storage",
                "conn_type": ConnectionType.NETWORK,
                "path": "//nas/archive",
                "description": "Network attached archive storage",
            },
        ]
        for c in demos:
            cid = c["name"].lower().replace(" ", "_")
            c["id"] = cid
            c["status"] = "connected"
            c["connected_at"] = datetime.now()
            c["file_count"] = 0
            self._connections[cid] = c

    def add_connection(self, name: str, conn_type: str = ConnectionType.LOCAL,
                       path: str = "", description: str = "") -> Dict[str, Any]:
        cid = name.lower().replace(" ", "_")
        connection = {
            "id": cid,
            "name": name,
            "conn_type": conn_type,
            "path": path,
            "description": description,
            "status": "disconnected",
            "connected_at": None,
            "file_count": 0,
        }
        self._connections[cid] = connection
        return connection

    def connect(self, connection_id: str) -> bool:
        conn = self._connections.get(connection_id)
        if not conn:
            return False
        conn["status"] = "connected"
        conn["connected_at"] = datetime.now()
        self._current_connection_id = connection_id
        return True

    def disconnect(self, connection_id: str) -> bool:
        conn = self._connections.get(connection_id)
        if not conn:
            return False
        conn["status"] = "disconnected"
        conn["connected_at"] = None
        if self._current_connection_id == connection_id:
            self._current_connection_id = None
        return True

    def remove_connection(self, connection_id: str) -> bool:
        if connection_id in self._connections:
            if self._current_connection_id == connection_id:
                self._current_connection_id = None
            del self._connections[connection_id]
            return True
        return False

    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        return self._connections.get(connection_id)

    def list_connections(self) -> List[Dict[str, Any]]:
        return list(self._connections.values())

    def get_type_info(self, conn_type: str) -> Dict[str, str]:
        return CONNECTION_TYPES.get(conn_type, CONNECTION_TYPES[ConnectionType.LOCAL])

    @property
    def current_connection(self) -> Optional[Dict[str, Any]]:
        if self._current_connection_id:
            return self._connections.get(self._current_connection_id)
        return None

    @property
    def current_connection_id(self) -> Optional[str]:
        return self._current_connection_id

    @current_connection_id.setter
    def current_connection_id(self, value: Optional[str]) -> None:
        self._current_connection_id = value

    def set_current_path(self, path: str) -> None:
        self._current_path = path

    @property
    def current_path(self) -> str:
        return self._current_path

    def browse_directory(self, path: str) -> List[Dict[str, Any]]:
        """Browse a directory and return its contents.

        Returns a list of file/directory entries with metadata.
        Safe — never executes business logic.
        """
        entries = []
        try:
            p = Path(path).expanduser().resolve()
            if p.exists() and p.is_dir():
                for child in sorted(p.iterdir()):
                    try:
                        stat = child.stat()
                        entries.append({
                            "name": child.name,
                            "path": str(child),
                            "is_dir": child.is_dir(),
                            "size": stat.st_size if child.is_file() else 0,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "ext": child.suffix if child.is_file() else "",
                        })
                    except OSError:
                        continue
        except (OSError, PermissionError):
            pass
        return entries
