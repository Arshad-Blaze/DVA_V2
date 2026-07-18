"""Tests for Administration Center (Sprint 9)."""

from unittest.mock import MagicMock
import pytest

from ui.services.admin_service import AdminService
from ui.controllers.admin_controller import AdminController
from ui.shared import WorkspaceContext


@pytest.fixture
def ctx():
    return WorkspaceContext()


@pytest.fixture
def svc(ctx):
    return AdminService(ctx)


@pytest.fixture
def notify():
    return MagicMock()


@pytest.fixture
def ctrl(svc, notify):
    return AdminController(svc, notify)


class TestAdminService:

    # ── System Health ────────────────────────────────────────

    def test_system_health_keys(self, svc):
        h = svc.system_health
        assert "cpu" in h
        assert "memory" in h
        assert "version" in h

    def test_system_health_cpu(self, svc):
        assert svc.system_health["cpu"]["status"] == "healthy"

    # ── Project History ──────────────────────────────────────

    def test_project_history(self, svc):
        h = svc.project_history
        assert len(h) == 2

    def test_select_project(self, svc):
        svc.select_project("Retail Sales Q1 2026")
        p = svc.selected_project
        assert p is not None
        assert p["name"] == "Retail Sales Q1 2026"

    def test_select_nonexistent_project(self, svc):
        svc.select_project("nonexistent")
        assert svc.selected_project is None

    # ── Execution History ────────────────────────────────────

    def test_execution_history(self, svc):
        h = svc.execution_history
        assert len(h) == 4

    def test_select_execution(self, svc):
        svc.select_execution("EXEC-001")
        e = svc.selected_execution
        assert e is not None
        assert e["execution_id"] == "EXEC-001"

    # ── Log Viewer ───────────────────────────────────────────

    def test_all_logs(self, svc):
        logs = svc.all_logs
        assert len(logs) == 10

    def test_log_sources(self, svc):
        sources = svc.log_sources
        assert "execution" in sources
        assert "validation" in sources

    def test_filtered_logs_default(self, svc):
        assert len(svc.filtered_logs) == 10

    def test_filter_logs_by_severity(self, svc):
        svc.set_log_severity("error")
        filtered = svc.filtered_logs
        assert all(l["severity"] == "error" for l in filtered)

    def test_filter_logs_by_source(self, svc):
        svc.set_log_source("validation")
        filtered = svc.filtered_logs
        assert all(l["source"] == "validation" for l in filtered)

    def test_filter_logs_by_search(self, svc):
        svc.set_log_search("UPC")
        filtered = svc.filtered_logs
        assert len(filtered) > 0
        svc.set_log_search("")

    def test_select_log(self, svc):
        svc.select_log(0)
        l = svc.selected_log
        assert l is not None

    def test_export_logs(self, svc):
        data = svc.export_logs()
        assert "Timestamp" in data

    # ── Diagnostics ──────────────────────────────────────────

    def test_diagnostics_keys(self, svc):
        d = svc.diagnostics
        assert d["architecture"]["status"] == "passed"
        assert d["contracts"]["status"] == "passed"

    # ── Storage ──────────────────────────────────────────────

    def test_storage_keys(self, svc):
        s = svc.storage
        assert "projects" in s
        assert "reports" in s
        assert "total_used_mb" in s

    # ── Settings ─────────────────────────────────────────────

    def test_default_settings(self, svc):
        s = svc.default_settings
        assert "application" in s
        assert "theme" in s

    def test_settings_initial(self, svc):
        s = svc.settings
        assert s["application"]["name"] == "DVA Platform"

    def test_update_setting(self, svc):
        svc.update_setting("theme", "dark_mode", True)
        s = svc.settings
        assert s["theme"]["dark_mode"] is True

    def test_reset_settings(self, svc):
        svc.update_setting("theme", "dark_mode", True)
        svc.reset_settings()
        s = svc.settings
        assert s["theme"]["dark_mode"] is False

    # ── Maintenance ──────────────────────────────────────────

    def test_maintenance_actions(self, svc):
        actions = svc.maintenance_actions
        assert len(actions) == 7

    def test_run_maintenance(self, svc):
        result = svc.run_maintenance("clear_cache")
        assert "completed successfully" in result

    def test_run_maintenance_unknown(self, svc):
        result = svc.run_maintenance("nonexistent")
        assert "Unknown" in result

    # ── About ────────────────────────────────────────────────

    def test_about(self, svc):
        a = svc.about
        assert a["version"] == "v2.0.0"
        assert "architecture" in a

    # ── Status Bar ───────────────────────────────────────────

    def test_status_bar(self, svc):
        s = svc.status_bar
        assert "health" in s
        assert "memory" in s
        assert "version" in s

    # ── Events ───────────────────────────────────────────────

    def test_on_change_callback(self, svc):
        cb = MagicMock()
        svc.on_change(cb)
        svc.select_execution("EXEC-001")
        cb.assert_called_once()


class TestAdminController:

    def test_system_health_delegates(self, ctrl, svc):
        assert ctrl.system_health == svc.system_health

    def test_project_history_delegates(self, ctrl, svc):
        assert ctrl.project_history == svc.project_history

    def test_select_project_delegates(self, ctrl, svc):
        ctrl.select_project("Retail Sales Q1 2026")
        assert svc.selected_project is not None

    def test_execution_history_delegates(self, ctrl, svc):
        assert ctrl.execution_history == svc.execution_history

    def test_select_execution_delegates(self, ctrl, svc):
        ctrl.select_execution("EXEC-001")
        assert svc.selected_execution is not None

    def test_filtered_logs_delegates(self, ctrl, svc):
        assert ctrl.filtered_logs == svc.filtered_logs

    def test_set_log_search_delegates(self, ctrl, svc):
        ctrl.set_log_search("test")
        assert svc._log_search == "test"

    def test_set_log_severity_delegates(self, ctrl, svc):
        ctrl.set_log_severity("error")
        assert svc._log_severity == "error"

    def test_set_log_source_delegates(self, ctrl, svc):
        ctrl.set_log_source("validation")
        assert svc._log_source == "validation"

    def test_select_log_delegates(self, ctrl, svc):
        ctrl.select_log(2)
        assert svc._selected_log == 2

    def test_export_logs_notifies(self, ctrl, notify):
        ctrl.export_logs()
        notify.success.assert_called_once()

    def test_diagnostics_delegates(self, ctrl, svc):
        assert ctrl.diagnostics == svc.diagnostics

    def test_storage_delegates(self, ctrl, svc):
        assert ctrl.storage == svc.storage

    def test_settings_delegates(self, ctrl, svc):
        assert ctrl.settings == svc.settings

    def test_update_setting_notifies(self, ctrl, notify):
        ctrl.update_setting("theme", "dark_mode", True)
        notify.info.assert_called_once()

    def test_reset_settings_notifies(self, ctrl, notify):
        ctrl.reset_settings()
        notify.info.assert_called_once()

    def test_maintenance_actions_delegates(self, ctrl, svc):
        assert ctrl.maintenance_actions == svc.maintenance_actions

    def test_run_maintenance_notifies(self, ctrl, notify):
        ctrl.run_maintenance("clear_cache")
        notify.success.assert_called_once()

    def test_about_delegates(self, ctrl, svc):
        assert ctrl.about == svc.about

    def test_status_bar_delegates(self, ctrl, svc):
        assert ctrl.status_bar == svc.status_bar
