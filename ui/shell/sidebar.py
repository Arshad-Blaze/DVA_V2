"""Shell — Navigation sidebar with pipeline state awareness."""

from ui.controllers.navigation_controller import NavigationController
from ui.shared import conn_svc, detection_svc, canonical_svc, preview_svc
from ui.shared import req_svc, op_svc, proc_svc, val_svc


FUNCTIONAL_WORKSPACES = {
    "home", "projects", "connection", "detection", "canonical",
    "preview", "requirement", "operation", "processing",
    "validation", "reports", "administration",
    "developer", "health", "settings", "help",
}


NAV_ITEMS = [
    ("", [
        ("home", "Home", "home"),
    ]),
    ("Project", [
        ("projects", "Projects", "folder"),
    ]),
    ("Workspaces", [
        ("connection", "Connection", "power"),
        ("detection", "Detection", "search"),
        ("canonical", "Canonical", "transform"),
        ("preview", "Preview", "preview"),
        ("requirement", "Requirement", "assignment"),
        ("operation", "Operation", "play_circle"),
        ("processing", "Processing", "calculate"),
        ("validation", "Validation", "verified"),
        ("reports", "Reports", "assessment"),
    ]),
    ("System", [
        ("administration", "Administration", "admin_panel_settings"),
        ("health", "Health", "monitor_heart"),
        ("developer", "Developer", "code"),
        ("settings", "Settings", "settings"),
        ("help", "Help", "help"),
    ]),
]


def _is_workspace_available(ws_id: str) -> bool:
    always_available = {"home", "projects", "connection", "administration",
                        "settings", "help", "health", "developer"}
    if ws_id in always_available:
        return True
    if ws_id == "detection":
        return conn_svc().current_connection is not None
    if ws_id == "canonical":
        return detection_svc().result is not None
    if ws_id == "preview":
        return canonical_svc().accepted
    if ws_id == "requirement":
        return preview_svc().is_approved
    if ws_id == "operation":
        return req_svc().is_confirmed
    if ws_id == "processing":
        return op_svc().is_approved
    if ws_id == "validation":
        return proc_svc().is_completed
    if ws_id == "reports":
        return val_svc().is_approved
    return True


def update_pipeline_state(nav_ctrl: NavigationController) -> None:
    for section_title, items in NAV_ITEMS:
        for ws_id, _, _ in items:
            available = _is_workspace_available(ws_id)
            if available:
                nav_ctrl._nav.enable(ws_id)
            else:
                nav_ctrl._nav.disable(ws_id)


WORKSPACE_TOOLTIPS = {
    "home": "Dashboard overview and quick actions",
    "projects": "Manage data projects",
    "connection": "Configure data source connections",
    "detection": "Discover file formats and structure",
    "canonical": "Map physical columns to business schema",
    "preview": "Review and approve transformed data",
    "requirement": "Define workflow requirements",
    "operation": "Orchestrate execution operations",
    "processing": "Run and monitor data processing",
    "validation": "Apply business rules and validate",
    "reports": "View reports and export data",
    "administration": "System administration and diagnostics",
    "health": "Monitor system health",
    "developer": "Developer tools and APIs",
    "settings": "Application settings",
    "help": "Documentation and support",
}


def create_sidebar(nav_ctrl: NavigationController, on_navigate) -> None:
    for section_title, items in NAV_ITEMS:
        if section_title:
            nav_ctrl.render_section(section_title)
        for ws_id, label, icon in items:
            is_active = nav_ctrl._nav.active == ws_id
            available = _is_workspace_available(ws_id)
            disabled = ws_id not in FUNCTIONAL_WORKSPACES or not available
            item = {
                "id": ws_id,
                "label": label,
                "icon": icon,
                "section": section_title,
            }
            nav_ctrl.register_workspace(ws_id, label, icon, section_title, disabled=disabled)
            rendered = nav_ctrl.render_nav_item(
                item, is_active,
                lambda w=ws_id: on_navigate(w),
            )
            tooltip = WORKSPACE_TOOLTIPS.get(ws_id, label)
            if rendered and hasattr(rendered, 'tooltip'):
                rendered.tooltip(tooltip)
