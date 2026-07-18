"""Shell — Navigation sidebar."""

from nicegui import ui
from ui.controllers.navigation_controller import NavigationController


FUNCTIONAL_WORKSPACES = {
    "home", "projects", "connection", "detection", "canonical",
    "preview", "requirement", "operation", "processing",
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
        ("downloads", "Downloads", "download"),
        ("history", "History", "history"),
        ("settings", "Settings", "settings"),
        ("help", "Help", "help"),
    ]),
]


def create_sidebar(nav_ctrl: NavigationController, on_navigate) -> None:
    for section_title, items in NAV_ITEMS:
        if section_title:
            nav_ctrl.render_section(section_title)
        for ws_id, label, icon in items:
            is_active = nav_ctrl._nav.active == ws_id
            disabled = ws_id not in FUNCTIONAL_WORKSPACES
            item = {
                "id": ws_id,
                "label": label,
                "icon": icon,
                "section": section_title,
            }
            nav_ctrl.register_workspace(ws_id, label, icon, section_title, disabled=disabled)
            nav_ctrl.render_nav_item(
                item, is_active,
                lambda w=ws_id: on_navigate(w),
            )
