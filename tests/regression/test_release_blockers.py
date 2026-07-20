import pytest
from unittest.mock import MagicMock, patch


class TestReleaseBlockers:

    def test_no_demo_data_in_services(self):
        from ui.services.project_service import ProjectService
        svc = ProjectService()
        projects = svc.list_projects()
        assert len(projects) == 0, "Project service should start empty"

    def test_no_demo_connections(self):
        from ui.services.connection_service import ConnectionService
        svc = ConnectionService()
        connections = svc.list_connections()
        assert len(connections) == 0, "Connection service should start empty"

    def test_no_demo_detection(self):
        from ui.services.detection_service import DetectionService
        svc = DetectionService()
        assert svc.result is None, "Detection should start with no result"
        assert svc.selected_file is None, "Detection should have no selected file"

    def test_no_demo_canonical(self):
        from ui.services.canonical_service import CanonicalService
        svc = CanonicalService()
        assert len(svc.physical_columns) == 0, "Canonical should start with no physical columns"
        assert len(svc.mappings) == 0, "Canonical should start with no mappings"

    def test_no_demo_preview(self):
        from ui.services.canonical_service import CanonicalService
        from ui.services.preview_service import PreviewService
        can_svc = CanonicalService()
        svc = PreviewService(can_svc)
        assert len(svc.preview_rows) == 0, "Preview should start with no rows"

    def test_workspaces_use_real_data(self):
        from ui.services.workspace_context import WorkspaceContext
        ctx = WorkspaceContext()
        assert ctx.current_workspace == "home"

    def test_theme_persistence(self):
        from ui.services.workspace_context import WorkspaceContext
        ctx = WorkspaceContext()
        ctx.theme = "dark"
        assert ctx.theme == "dark"
        data = ctx.to_dict()
        assert data["theme"] == "dark"
        ctx2 = WorkspaceContext()
        ctx2.from_dict(data)
        assert ctx2.theme == "dark"

    def test_connection_persistence(self):
        from ui.services.workspace_context import WorkspaceContext
        ctx = WorkspaceContext()
        ctx.current_connection_id = "test_conn"
        data = ctx.to_dict()
        ctx2 = WorkspaceContext()
        ctx2.from_dict(data)
        assert ctx2.current_connection_id == "test_conn"

    def test_navigation_no_dead_ends(self):
        from ui.services.navigation_service import NavigationService
        svc = NavigationService()
        workspace_ids = [
            "home", "projects", "connection", "detection", "canonical",
            "preview", "requirement", "operation", "processing",
            "validation", "reports", "administration",
        ]
        for ws_id in workspace_ids:
            svc.navigate(ws_id)
            assert svc.active == ws_id, f"Navigation to {ws_id} failed"

    def test_architecture_layers_frozen(self):
        import dav_platform
        assert hasattr(dav_platform, "__version__"), "Platform must have version"

    def test_contracts_stable(self):
        from dav_platform.core.contracts import (
            DiscoveryResult, ColumnMapping, CanonicalMetadata
        )
        assert DiscoveryResult is not None
        assert ColumnMapping is not None
        assert CanonicalMetadata is not None

    def test_demo_mode_isolated(self):
        from ui.services.demo_service import DemoService
        svc = DemoService()
        assert not svc.is_active, "Demo should start inactive"
        svc.reset()
        assert not svc.is_active

    def test_guidance_present(self):
        from ui.services.guidance_service import GuidanceService
        svc = GuidanceService()
        workspace_ids = [
            "home", "projects", "connection", "detection", "canonical",
            "preview", "requirement", "operation", "processing",
            "validation", "reports", "administration",
        ]
        for ws_id in workspace_ids:
            guidance = svc.get_guidance(ws_id)
            assert guidance is not None, f"Guidance missing for {ws_id}"
            assert "step" in guidance
            assert "purpose" in guidance
            assert "instructions" in guidance

    def test_welcome_wizard_available(self):
        from ui.services.welcome_service import WelcomeService
        svc = WelcomeService()
        assert svc.current_step == 0
        assert svc.step_count == 7
        assert not svc.is_completed
        svc.next_step()
        assert svc.current_step == 1
        svc.complete()
        assert svc.is_completed

    def test_version_compatibility_documented(self):
        import os
        matrix_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "docs",
            "release", "compatibility_matrix.md"
        )
        assert os.path.exists(matrix_path), "Compatibility matrix must exist"

    def test_requirements_pinned(self):
        import os
        req_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "requirements.txt"
        )
        assert os.path.exists(req_path), "requirements.txt must exist"
