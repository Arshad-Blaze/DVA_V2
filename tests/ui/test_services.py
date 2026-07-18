"""UI Tests — Services (Session, Navigation, Notification, Theme)."""

import pytest
from ui.services.session_service import SessionService
from ui.services.navigation_service import NavigationService
from ui.services.notification_service import NotificationService, NotificationType
from ui.services.theme_service import ThemeService


class TestSessionService:
    def test_default_state(self):
        svc = SessionService()
        assert svc.current_workspace == "home"
        assert svc.execution_status == "idle"
        assert svc.theme == "light"
        assert svc.current_project == ""

    def test_set_workspace(self):
        svc = SessionService()
        svc.current_workspace = "connection"
        assert svc.current_workspace == "connection"

    def test_nav_history(self):
        svc = SessionService()
        svc.current_workspace = "a"
        svc.current_workspace = "b"
        svc.current_workspace = "c"
        assert svc.nav_back() == "b"
        assert svc.nav_back() == "a"
        assert svc.nav_back() is not None

    def test_execution_status(self):
        svc = SessionService()
        svc.execution_status = "running"
        assert svc.execution_status == "running"

    def test_theme_toggle(self):
        svc = SessionService()
        svc.theme = "dark"
        assert svc.theme == "dark"
        svc.theme = "light"
        assert svc.theme == "light"

    def test_sidebar_preference(self):
        svc = SessionService()
        assert svc.sidebar_collapsed is False
        svc.sidebar_collapsed = True
        assert svc.sidebar_collapsed is True

    def test_inspector_preference(self):
        svc = SessionService()
        assert svc.inspector_visible is True
        svc.inspector_visible = False
        assert svc.inspector_visible is False

    def test_workspace_params(self):
        svc = SessionService()
        svc.set_workspace_param("key1", "value1")
        assert svc.get_workspace_param("key1") == "value1"
        assert svc.get_workspace_param("nonexistent", "default") == "default"
        svc.clear_workspace_params()
        assert svc.get_workspace_param("key1") is None

    def test_reset(self):
        svc = SessionService()
        svc.current_workspace = "processing"
        svc.execution_status = "running"
        svc.set_workspace_param("x", 1)
        svc.reset()
        assert svc.current_workspace == "home"
        assert svc.execution_status == "idle"
        assert svc.get_workspace_param("x") is None


class TestNavigationService:
    def test_default_state(self):
        svc = NavigationService()
        assert svc.active == "home"
        assert svc.items == []

    def test_register_and_list(self):
        svc = NavigationService()
        svc.register({"id": "home", "label": "Home"})
        svc.register({"id": "conn", "label": "Connection"})
        assert len(svc.items) == 2

    def test_navigate(self):
        svc = NavigationService()
        svc.navigate("processing")
        assert svc.active == "processing"

    def test_navigate_disabled(self):
        svc = NavigationService()
        svc.disable("processing")
        svc.navigate("processing")
        assert svc.active == "home"

    def test_disable_enable(self):
        svc = NavigationService()
        svc.disable("processing")
        assert svc.is_disabled("processing") is True
        svc.enable("processing")
        assert svc.is_disabled("processing") is False

    def test_on_change_callback(self):
        svc = NavigationService()
        called = []
        def callback(ws_id):
            called.append(ws_id)
        svc.on_change(callback)
        svc.navigate("validation")
        assert called == ["validation"]

    def test_reset(self):
        svc = NavigationService()
        svc.navigate("processing")
        svc.disable("output")
        svc.reset()
        assert svc.active == "home"
        assert svc.is_disabled("output") is False


class TestNotificationService:
    def test_notify(self):
        svc = NotificationService()
        svc.notify("Test message", NotificationType.INFO)
        assert len(svc.notifications) == 1
        assert svc.notifications[0]["message"] == "Test message"

    def test_notification_types(self):
        svc = NotificationService()
        svc.success("OK")
        svc.warning("Careful")
        svc.error("Failed")
        svc.info("Info")
        svc.progress("Working")
        assert len(svc.notifications) == 5

    def test_on_notification_callback(self):
        svc = NotificationService()
        received = []
        svc.on_notification(lambda entry: received.append(entry))
        svc.success("Done")
        assert len(received) == 1
        assert received[0]["type_value"] == "success"

    def test_clear(self):
        svc = NotificationService()
        svc.info("Test")
        svc.clear()
        assert len(svc.notifications) == 0


class TestThemeService:
    def test_default_is_light(self):
        svc = ThemeService()
        assert svc.is_dark is False

    def test_toggle(self):
        svc = ThemeService()
        svc.toggle()
        assert svc.is_dark is True
        svc.toggle()
        assert svc.is_dark is False

    def test_set_dark(self):
        svc = ThemeService()
        svc.set_dark(True)
        assert svc.is_dark is True

    def test_on_change_callback(self):
        svc = ThemeService()
        called = []
        svc.on_change(lambda dark: called.append(dark))
        svc.toggle()
        assert called == [True]
