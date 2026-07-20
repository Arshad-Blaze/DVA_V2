"""Connection service — manages data source connections.

Supports persistence via optional PersistenceService injection.
If no persistence is provided, operates in-memory (backward compatible).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ConnectionType:
    LOCAL = "local"
    SSH = "ssh"
    MFT = "mft"


CONNECTION_TYPES = {
    ConnectionType.LOCAL: {"label": "Local Filesystem", "icon": "folder", "color": "primary"},
    ConnectionType.SSH: {"label": "SSH Connection", "icon": "terminal", "color": "info"},
    ConnectionType.MFT: {"label": "MFT Connection", "icon": "sync_alt", "color": "warning"},
}

CONNECTION_FORMS = {
    ConnectionType.LOCAL: {
        "fields": [
            {"key": "directory", "label": "Directory", "type": "directory", "required": True},
            {"key": "description", "label": "Description", "type": "text", "required": False},
        ],
        "actions": ["browse", "test"],
    },
    ConnectionType.SSH: {
        "fields": [
            {"key": "host", "label": "Host", "type": "text", "required": True},
            {"key": "port", "label": "Port", "type": "number", "required": True, "default": 22},
            {"key": "username", "label": "Username", "type": "text", "required": True},
            {"key": "password", "label": "Password", "type": "password", "required": False},
            {"key": "private_key", "label": "Private Key", "type": "file", "required": False},
            {"key": "remote_directory", "label": "Remote Directory", "type": "text", "required": False},
            {"key": "description", "label": "Description", "type": "text", "required": False},
        ],
        "actions": ["test"],
    },
    ConnectionType.MFT: {
        "fields": [
            {"key": "server", "label": "Server", "type": "text", "required": True},
            {"key": "port", "label": "Port", "type": "number", "required": True, "default": 21},
            {"key": "protocol", "label": "Protocol", "type": "select", "required": True,
             "options": ["SFTP", "FTPS", "FTPES", "HTTPS"]},
            {"key": "username", "label": "Username", "type": "text", "required": True},
            {"key": "password", "label": "Password", "type": "password", "required": True},
            {"key": "remote_directory", "label": "Remote Directory", "type": "text", "required": False},
            {"key": "polling_interval", "label": "Polling Interval (min)", "type": "number", "required": False, "default": 5},
            {"key": "description", "label": "Description", "type": "text", "required": False},
        ],
        "actions": ["test"],
    },
}


class ConnectionService:
    """Manages connection state and file browsing within the UI session.

    When a PersistenceService is provided, all CRUD operations
    automatically persist to disk.
    """

    def __init__(self, persistence=None, context=None):
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._current_connection_id: Optional[str] = None
        self._current_path: str = "/"
        self._persistence = persistence
        self._context = context

        if self._persistence:
            loaded = self._persistence.load_connections()
            for c in loaded:
                cid = c.get("id")
                if cid:
                    self._connections[cid] = c

    def add_connection(self, name: str, conn_type: str = ConnectionType.LOCAL,
                       path: str = "", description: str = "", **kwargs) -> Dict[str, Any]:
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
        connection.update(kwargs)
        self._connections[cid] = connection
        self._persist()
        return connection

    def update_connection(self, connection_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        conn = self._connections.get(connection_id)
        if not conn:
            return None
        conn.update(kwargs)
        self._persist()
        return conn

    def duplicate_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        original = self._connections.get(connection_id)
        if not original:
            return None
        new_name = f"{original['name']} (Copy)"
        cid = new_name.lower().replace(" ", "_")
        connection = dict(original)
        connection["id"] = cid
        connection["name"] = new_name
        connection["status"] = "disconnected"
        connection["connected_at"] = None
        connection["file_count"] = 0
        self._connections[cid] = connection
        self._persist()
        return connection

    def connect(self, connection_id: str) -> bool:
        conn = self._connections.get(connection_id)
        if not conn:
            return False
        conn["status"] = "connected"
        conn["connected_at"] = datetime.now()
        self._current_connection_id = connection_id
        if self._context:
            self._context.current_connection_id = connection_id
            self._context.add_recent_connection(connection_id)
        self._persist()
        return True

    def disconnect(self, connection_id: str) -> bool:
        conn = self._connections.get(connection_id)
        if not conn:
            return False
        conn["status"] = "disconnected"
        conn["connected_at"] = None
        if self._current_connection_id == connection_id:
            self._current_connection_id = None
            if self._context:
                self._context.current_connection_id = None
        self._persist()
        return True

    def remove_connection(self, connection_id: str) -> bool:
        if connection_id in self._connections:
            if self._current_connection_id == connection_id:
                self._current_connection_id = None
                if self._context:
                    self._context.current_connection_id = None
            del self._connections[connection_id]
            self._persist()
            return True
        return False

    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        return self._connections.get(connection_id)

    def list_connections(self) -> List[Dict[str, Any]]:
        return list(self._connections.values())

    def get_type_info(self, conn_type: str) -> Dict[str, str]:
        return CONNECTION_TYPES.get(conn_type, CONNECTION_TYPES[ConnectionType.LOCAL])

    def get_form_config(self, conn_type: str) -> Dict[str, Any]:
        return CONNECTION_FORMS.get(conn_type, CONNECTION_FORMS[ConnectionType.LOCAL])

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
        if self._context:
            self._context.current_connection_id = value

    def set_current_path(self, path: str) -> None:
        self._current_path = path

    @property
    def current_path(self) -> str:
        return self._current_path

    def browse_directory(self, path: str) -> List[Dict[str, Any]]:
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

    def _persist(self) -> None:
        if self._persistence:
            self._persistence.save_connections(self.list_connections())
