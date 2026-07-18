"""UI Tests — Connection Service & Controller (Sprint 2B)."""

import pytest
from ui.services.connection_service import ConnectionService, ConnectionType
from ui.controllers.connection_controller import ConnectionController
from ui.services.notification_service import NotificationService


class TestConnectionService:
    def test_default_state(self):
        svc = ConnectionService()
        conns = svc.list_connections()
        assert len(conns) == 3  # 3 demo connections seeded
        assert svc.current_connection_id is None
        assert svc.current_connection is None

    def test_add_connection(self):
        svc = ConnectionService()
        c = svc.add_connection("Test Source", ConnectionType.LOCAL, "/data/test", "Test")
        assert c["name"] == "Test Source"
        assert c["id"] == "test_source"
        assert c["status"] == "disconnected"
        assert len(svc.list_connections()) == 4

    def test_connect(self):
        svc = ConnectionService()
        svc.add_connection("My Conn", path="/tmp")
        result = svc.connect("my_conn")
        assert result is True
        c = svc.get_connection("my_conn")
        assert c["status"] == "connected"
        assert svc.current_connection_id == "my_conn"

    def test_connect_nonexistent(self):
        svc = ConnectionService()
        result = svc.connect("nope")
        assert result is False

    def test_disconnect(self):
        svc = ConnectionService()
        svc.add_connection("My Conn", path="/tmp")
        svc.connect("my_conn")
        svc.disconnect("my_conn")
        c = svc.get_connection("my_conn")
        assert c["status"] == "disconnected"
        assert svc.current_connection_id is None

    def test_remove_connection(self):
        svc = ConnectionService()
        svc.add_connection("Remove Me", path="/tmp")
        svc.connect("remove_me")
        result = svc.remove_connection("remove_me")
        assert result is True
        assert svc.get_connection("remove_me") is None
        assert svc.current_connection_id is None

    def test_get_type_info(self):
        svc = ConnectionService()
        info = svc.get_type_info(ConnectionType.LOCAL)
        assert info["label"] == "Local Filesystem"
        assert info["icon"] == "folder"

    def test_browse_directory(self):
        svc = ConnectionService()
        entries = svc.browse_directory("/tmp")
        assert isinstance(entries, list)

    def test_browse_nonexistent(self):
        svc = ConnectionService()
        entries = svc.browse_directory("/nonexistent_path_xyz")
        assert entries == []

    def test_current_path(self):
        svc = ConnectionService()
        assert svc.current_path == "/"
        svc.set_current_path("/data")
        assert svc.current_path == "/data"


class TestConnectionController:
    def test_add_empty_name_warns(self):
        notify = NotificationService()
        svc = ConnectionService()
        ctrl = ConnectionController(svc, notify)
        result = ctrl.add_connection("")
        assert result is None
        assert len(notify.notifications) == 1

    def test_add_valid(self):
        notify = NotificationService()
        svc = ConnectionService()
        ctrl = ConnectionController(svc, notify)
        result = ctrl.add_connection("New Source", ConnectionType.LOCAL, "/path")
        assert result is not None
        assert result["name"] == "New Source"

    def test_connect(self):
        notify = NotificationService()
        svc = ConnectionService()
        ctrl = ConnectionController(svc, notify)
        svc.add_connection("Test", path="/tmp")
        result = ctrl.connect("test")
        assert result is True
        assert svc.current_connection_id == "test"

    def test_disconnect(self):
        notify = NotificationService()
        svc = ConnectionService()
        ctrl = ConnectionController(svc, notify)
        svc.add_connection("Test", path="/tmp")
        svc.connect("test")
        ctrl.disconnect("test")
        assert svc.current_connection_id is None

    def test_remove(self):
        notify = NotificationService()
        svc = ConnectionService()
        ctrl = ConnectionController(svc, notify)
        svc.add_connection("Test", path="/tmp")
        svc.connect("test")
        ctrl.remove_connection("test")
        assert svc.get_connection("test") is None
