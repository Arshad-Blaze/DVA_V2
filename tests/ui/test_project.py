"""UI Tests — Project Service & Controller (Sprint 2A)."""

import pytest
from ui.services.project_service import ProjectService
from ui.controllers.project_controller import ProjectController
from ui.services.notification_service import NotificationService


class TestProjectService:
    def test_default_state(self):
        svc = ProjectService()
        projects = svc.list_projects()
        assert len(projects) == 3  # 3 demo projects seeded
        assert svc.current_project_id is None
        assert svc.current_project is None

    def test_create_project(self):
        svc = ProjectService()
        p = svc.create_project("Test Project", "A test", "/data/test")
        assert p["name"] == "Test Project"
        assert p["id"] == "test_project"
        assert p["source"] == "/data/test"
        assert svc.current_project_id == "test_project"

    def test_open_project(self):
        svc = ProjectService()
        p = svc.open_project("retail_sales_q2")
        assert p is not None
        assert p["name"] == "Retail Sales Q2"
        assert svc.current_project_id == "retail_sales_q2"

    def test_open_nonexistent(self):
        svc = ProjectService()
        p = svc.open_project("nonexistent")
        assert p is None

    def test_rename_project(self):
        svc = ProjectService()
        svc.open_project("retail_sales_q2")
        result = svc.rename_project("retail_sales_q2", "Sales Q2 2026")
        assert result is True
        p = svc.get_project("sales_q2_2026")
        assert p is not None
        assert p["name"] == "Sales Q2 2026"

    def test_delete_project(self):
        svc = ProjectService()
        svc.open_project("retail_sales_q2")
        result = svc.delete_project("retail_sales_q2")
        assert result is True
        assert svc.get_project("retail_sales_q2") is None
        assert svc.current_project_id is None

    def test_close_project(self):
        svc = ProjectService()
        svc.open_project("retail_sales_q2")
        assert svc.current_project_id is not None
        svc.close_project()
        assert svc.current_project_id is None

    def test_recent_projects(self):
        svc = ProjectService()
        recent = svc.recent_projects(2)
        assert len(recent) == 2

    def test_list_projects_order(self):
        svc = ProjectService()
        svc.create_project("ZZZ Project")
        projects = svc.list_projects()
        # Most recently modified first
        assert projects[0]["id"] == "zzz_project"


class TestProjectController:
    def test_create_empty_name_warns(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        result = ctrl.create_project("")
        assert result is None
        assert len(notify.notifications) == 1

    def test_create_valid(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        result = ctrl.create_project("New Project", "desc", "/path")
        assert result is not None
        assert result["name"] == "New Project"
        assert len(notify.notifications) == 1

    def test_open(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        p = ctrl.open_project("retail_sales_q2")
        assert p is not None
        assert len(notify.notifications) == 1

    def test_open_nonexistent(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        p = ctrl.open_project("nope")
        assert p is None
        assert len(notify.notifications) == 1  # error notification

    def test_delete(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        ctrl.open_project("retail_sales_q2")
        ctrl.delete_project("retail_sales_q2")
        assert svc.get_project("retail_sales_q2") is None

    def test_rename_empty(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        ctrl.open_project("retail_sales_q2")
        ctrl.rename_project("retail_sales_q2", "")
        p = svc.get_project("retail_sales_q2")
        assert p is not None
        assert p["name"] == "Retail Sales Q2"

    def test_close(self):
        notify = NotificationService()
        svc = ProjectService()
        ctrl = ProjectController(svc, notify)
        ctrl.open_project("retail_sales_q2")
        ctrl.close_project()
        assert svc.current_project_id is None
