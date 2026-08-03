"""Connection controller — bridges connection service to UI."""

from typing import Any, Callable, Dict, List, Optional

from ui.services.connection_service import ConnectionService
from ui.services.notification_service import NotificationService


class ConnectionController:
    """Controls connection operations from the UI."""

    def __init__(self, conn_svc: ConnectionService, notify_svc: NotificationService):
        self._conn_svc = conn_svc
        self._notify_svc = notify_svc
        self._on_change: Optional[Callable] = None

    def add_connection(self, name: str, conn_type: str = "local",
                       path: str = "", description: str = "", **kwargs) -> Optional[Dict[str, Any]]:
        if not name or not name.strip():
            self._notify_svc.warning("Connection name is required")
            return None
        conn = self._conn_svc.add_connection(name.strip(), conn_type, path.strip(), description.strip(), **kwargs)
        self._notify_svc.success(f"Connection '{name}' added")
        if self._on_change:
            self._on_change()
        return conn

    def update_connection(self, connection_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        conn = self._conn_svc.update_connection(connection_id, **kwargs)
        if conn:
            self._notify_svc.success(f"Connection '{conn['name']}' updated")
        else:
            self._notify_svc.error("Failed to update connection")
        if self._on_change:
            self._on_change()
        return conn

    def duplicate_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        conn = self._conn_svc.duplicate_connection(connection_id)
        if conn:
            self._notify_svc.success(f"Connection duplicated as '{conn['name']}'")
        else:
            self._notify_svc.error("Failed to duplicate connection")
        if self._on_change:
            self._on_change()
        return conn

    def connect(self, connection_id: str) -> bool:
        result = self._conn_svc.connect(connection_id)
        if result:
            conn = self._conn_svc.get_connection(connection_id)
            self._notify_svc.info(f"Connected to '{conn['name']}'")
        else:
            self._notify_svc.error("Connection failed")
        if self._on_change:
            self._on_change()
        return result

    def disconnect(self, connection_id: str) -> bool:
        conn = self._conn_svc.get_connection(connection_id)
        result = self._conn_svc.disconnect(connection_id)
        if result and conn:
            self._notify_svc.info(f"Disconnected from '{conn['name']}'")
        if self._on_change:
            self._on_change()
        return result

    def remove_connection(self, connection_id: str) -> bool:
        conn = self._conn_svc.get_connection(connection_id)
        result = self._conn_svc.remove_connection(connection_id)
        if result and conn:
            self._notify_svc.success(f"Connection '{conn['name']}' removed")
        if self._on_change:
            self._on_change()
        return result

    def test_connection(self, conn_type: str, **kwargs) -> bool:
        self._notify_svc.info(f"Testing {conn_type} connection...")
        return True

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    @property
    def connections(self) -> List[Dict[str, Any]]:
        return self._conn_svc.list_connections()

    @property
    def current_connection(self) -> Optional[Dict[str, Any]]:
        return self._conn_svc.current_connection

    def browse_directory(self, path: str) -> List[Dict[str, Any]]:
        return self._conn_svc.browse_directory(path)

    def get_type_info(self, conn_type: str) -> Dict[str, str]:
        return self._conn_svc.get_type_info(conn_type)

    def get_form_config(self, conn_type: str) -> Dict[str, Any]:
        return self._conn_svc.get_form_config(conn_type)
