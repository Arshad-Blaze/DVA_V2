"""Shared UI service instances — global singletons.

All workspaces and controllers import from here to access the same
service instances that app.py creates. Prevents duplicate state.
"""

from typing import Any, Callable, Dict, List, Optional

from ui.services.project_service import ProjectService
from ui.services.connection_service import ConnectionService
from ui.services.session_service import SessionService
from ui.services.navigation_service import NavigationService
from ui.services.notification_service import NotificationService
from ui.services.theme_service import ThemeService
from ui.controllers.project_controller import ProjectController
from ui.controllers.connection_controller import ConnectionController
from ui.controllers.navigation_controller import NavigationController
from ui.controllers.session_controller import SessionController
from ui.controllers.workspace_controller import WorkspaceController
from ui.services.persistence_service import PersistenceService
from ui.services.storage_service import StorageService
from ui.services.migration_service import MigrationService
from ui.services.workspace_context import WorkspaceContext
from ui.services.detection_service import DetectionService
from ui.controllers.detection_controller import DetectionController
from ui.services.canonical_service import CanonicalService
from ui.controllers.canonical_controller import CanonicalController
from ui.services.preview_service import PreviewService
from ui.controllers.preview_controller import PreviewController
from ui.services.requirement_service import RequirementService
from ui.controllers.requirement_controller import RequirementController
from ui.services.operation_service import OperationService
from ui.controllers.operation_controller import OperationController
from ui.services.processing_service import ProcessingService
from ui.controllers.processing_controller import ProcessingController
from ui.services.validation_service import ValidationService
from ui.controllers.validation_controller import ValidationController
from ui.services.reports_service import ReportsService
from ui.controllers.reports_controller import ReportsController
from ui.services.admin_service import AdminService
from ui.controllers.admin_controller import AdminController


# --- Lazy-initialized singletons ---

_context: Optional[WorkspaceContext] = None
_storage: Optional[StorageService] = None
_migration: Optional[MigrationService] = None
_persistence: Optional[PersistenceService] = None

# Global navigation handler (wired from app.py)
_on_navigate_handler: Optional[Callable[[str], None]] = None

def set_navigate_handler(handler: Callable[[str], None]) -> None:
    global _on_navigate_handler
    _on_navigate_handler = handler

def navigate_to(workspace_id: str) -> None:
    if _on_navigate_handler:
        _on_navigate_handler(workspace_id)

_session_svc: Optional[SessionService] = None
_project_svc: Optional[ProjectService] = None
_conn_svc: Optional[ConnectionService] = None
_nav_svc: Optional[NavigationService] = None
_notify_svc: Optional[NotificationService] = None
_theme_svc: Optional[ThemeService] = None
_detection_svc: Optional[DetectionService] = None
_canonical_svc: Optional[CanonicalService] = None
_preview_svc: Optional[PreviewService] = None
_req_svc: Optional[RequirementService] = None
_op_svc: Optional[OperationService] = None
_proc_svc: Optional[ProcessingService] = None
_val_svc: Optional[ValidationService] = None

_session_ctrl: Optional[SessionController] = None
_nav_ctrl: Optional[NavigationController] = None
_ws_ctrl: Optional[WorkspaceController] = None
_project_ctrl: Optional[ProjectController] = None
_conn_ctrl: Optional[ConnectionController] = None
_detection_ctrl: Optional[DetectionController] = None
_canonical_ctrl: Optional[CanonicalController] = None
_preview_ctrl: Optional[PreviewController] = None
_req_ctrl: Optional[RequirementController] = None
_op_ctrl: Optional[OperationController] = None
_proc_ctrl: Optional[ProcessingController] = None
_val_ctrl: Optional[ValidationController] = None
_rep_svc: Optional[ReportsService] = None
_rep_ctrl: Optional[ReportsController] = None
_adm_svc: Optional[AdminService] = None
_adm_ctrl: Optional[AdminController] = None


def init_all(with_persistence: bool = True) -> None:
    """Initialize all shared services. Called once from app.py."""
    global _context, _storage, _migration, _persistence
    global _session_svc, _project_svc, _conn_svc, _nav_svc, _notify_svc, _theme_svc
    global _session_ctrl, _nav_ctrl, _ws_ctrl, _project_ctrl, _conn_ctrl
    global _detection_svc, _detection_ctrl
    global _canonical_svc, _canonical_ctrl
    global _preview_svc, _preview_ctrl
    global _req_svc, _req_ctrl
    global _op_svc, _op_ctrl
    global _proc_svc, _proc_ctrl
    global _val_svc, _val_ctrl
    global _rep_svc, _rep_ctrl
    global _adm_svc, _adm_ctrl

    _context = WorkspaceContext()
    _storage = StorageService()
    _migration = MigrationService(_storage)
    _persistence = PersistenceService(_storage, _migration, _context)

    if with_persistence:
        _persistence.run_migrations()
        _persistence.restore_session()

    _session_svc = SessionService(_context)
    _nav_svc = NavigationService()
    _notify_svc = NotificationService()
    _theme_svc = ThemeService()

    _project_svc = ProjectService(_persistence, _context)
    _conn_svc = ConnectionService(_persistence, _context)

    _session_ctrl = SessionController(_session_svc, _theme_svc)
    _nav_ctrl = NavigationController(_nav_svc)
    _ws_ctrl = WorkspaceController(_session_svc, _nav_svc)
    _project_ctrl = ProjectController(_project_svc, _notify_svc)
    _conn_ctrl = ConnectionController(_conn_svc, _notify_svc)
    _detection_svc = DetectionService(_context)
    _detection_ctrl = DetectionController(_detection_svc, _notify_svc)
    _canonical_svc = CanonicalService(_context)
    _canonical_ctrl = CanonicalController(_canonical_svc, _notify_svc)
    _preview_svc = PreviewService(_canonical_svc)
    _preview_ctrl = PreviewController(_preview_svc, _notify_svc)
    _req_svc = RequirementService(_context)
    _req_ctrl = RequirementController(_req_svc, _notify_svc)
    _op_svc = OperationService(_req_svc)
    _op_ctrl = OperationController(_op_svc, _notify_svc)
    _proc_svc = ProcessingService(_op_svc)
    _proc_ctrl = ProcessingController(_proc_svc, _notify_svc)
    _val_svc = ValidationService(_context)
    _val_ctrl = ValidationController(_val_svc, _notify_svc)
    _rep_svc = ReportsService(_context)
    _rep_ctrl = ReportsController(_rep_svc, _notify_svc)
    _adm_svc = AdminService(_context)
    _adm_ctrl = AdminController(_adm_svc, _notify_svc)

    # Update session service theme from the context
    is_dark = _context.theme == "dark" if _context else False
    if is_dark and _theme_svc:
        _theme_svc.set_dark(True)


def context() -> WorkspaceContext:
    assert _context is not None
    return _context

def storage() -> StorageService:
    assert _storage is not None
    return _storage

def persistence() -> PersistenceService:
    assert _persistence is not None
    return _persistence

def session_svc() -> SessionService:
    assert _session_svc is not None
    return _session_svc

def project_svc() -> ProjectService:
    assert _project_svc is not None
    return _project_svc

def conn_svc() -> ConnectionService:
    assert _conn_svc is not None
    return _conn_svc

def nav_svc() -> NavigationService:
    assert _nav_svc is not None
    return _nav_svc

def notify_svc() -> NotificationService:
    assert _notify_svc is not None
    return _notify_svc

def theme_svc() -> ThemeService:
    assert _theme_svc is not None
    return _theme_svc

def session_ctrl() -> SessionController:
    assert _session_ctrl is not None
    return _session_ctrl

def nav_ctrl() -> NavigationController:
    assert _nav_ctrl is not None
    return _nav_ctrl

def ws_ctrl() -> WorkspaceController:
    assert _ws_ctrl is not None
    return _ws_ctrl

def project_ctrl() -> ProjectController:
    assert _project_ctrl is not None
    return _project_ctrl

def conn_ctrl() -> ConnectionController:
    assert _conn_ctrl is not None
    return _conn_ctrl

def detection_svc() -> DetectionService:
    assert _detection_svc is not None
    return _detection_svc

def detection_ctrl() -> DetectionController:
    assert _detection_ctrl is not None
    return _detection_ctrl

def canonical_svc() -> CanonicalService:
    assert _canonical_svc is not None
    return _canonical_svc

def canonical_ctrl() -> CanonicalController:
    assert _canonical_ctrl is not None
    return _canonical_ctrl

def preview_svc() -> PreviewService:
    assert _preview_svc is not None
    return _preview_svc

def preview_ctrl() -> PreviewController:
    assert _preview_ctrl is not None
    return _preview_ctrl

def req_svc() -> RequirementService:
    assert _req_svc is not None
    return _req_svc

def req_ctrl() -> RequirementController:
    assert _req_ctrl is not None
    return _req_ctrl

def op_svc() -> OperationService:
    assert _op_svc is not None
    return _op_svc

def op_ctrl() -> OperationController:
    assert _op_ctrl is not None
    return _op_ctrl

def proc_svc() -> ProcessingService:
    assert _proc_svc is not None
    return _proc_svc

def proc_ctrl() -> ProcessingController:
    assert _proc_ctrl is not None
    return _proc_ctrl

def val_svc() -> ValidationService:
    assert _val_svc is not None
    return _val_svc

def val_ctrl() -> ValidationController:
    assert _val_ctrl is not None
    return _val_ctrl

def rep_svc() -> ReportsService:
    assert _rep_svc is not None
    return _rep_svc

def reports_ctrl() -> ReportsController:
    assert _rep_ctrl is not None
    return _rep_ctrl

def rep_ctrl() -> ReportsController:
    return reports_ctrl()

def admin_svc() -> AdminService:
    assert _adm_svc is not None
    return _adm_svc

def admin_ctrl() -> AdminController:
    assert _adm_ctrl is not None
    return _adm_ctrl
