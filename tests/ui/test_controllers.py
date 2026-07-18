"""UI Tests — Controllers (Navigation, Session)."""

import pytest
from ui.controllers.navigation_controller import NavigationController
from ui.controllers.session_controller import SessionController
from ui.controllers.workspace_controller import WorkspaceController
from ui.services.navigation_service import NavigationService
from ui.services.session_service import SessionService
from ui.services.theme_service import ThemeService


class TestNavigationController:
    def test_register_workspace(self):
        nav_svc = NavigationService()
        ctrl = NavigationController(nav_svc)
        ctrl.register_workspace("home", "Home", "home")
        assert len(nav_svc.items) == 1

    def test_register_disabled(self):
        nav_svc = NavigationService()
        ctrl = NavigationController(nav_svc)
        ctrl.register_workspace("conn", "Connection", "power", disabled=True)
        assert nav_svc.is_disabled("conn") is True

    def test_navigate(self):
        nav_svc = NavigationService()
        ctrl = NavigationController(nav_svc)
        ctrl.register_workspace("home", "Home", "home")
        ctrl.register_workspace("proc", "Processing", "calculate")
        ctrl.navigate("proc")
        assert nav_svc.active == "proc"


class TestSessionController:
    def test_toggle_theme(self):
        session = SessionService()
        theme = ThemeService()
        ctrl = SessionController(session, theme)
        ctrl.toggle_theme()
        assert theme.is_dark is True
        assert session.theme == "dark"

    def test_toggle_sidebar(self):
        session = SessionService()
        theme = ThemeService()
        ctrl = SessionController(session, theme)
        ctrl.toggle_sidebar()
        assert session.sidebar_collapsed is True
        ctrl.toggle_sidebar()
        assert session.sidebar_collapsed is False

    def test_toggle_inspector(self):
        session = SessionService()
        theme = ThemeService()
        ctrl = SessionController(session, theme)
        ctrl.toggle_inspector()
        assert session.inspector_visible is False


class TestWorkspaceController:
    def test_register_and_render(self):
        session = SessionService()
        nav = NavigationService()
        ctrl = WorkspaceController(session, nav)
        rendered = []

        def home_render():
            rendered.append("home_rendered")

        ctrl.register("home", home_render)
        assert ctrl._registry["home"] is home_render
