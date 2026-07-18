"""Navigation controller — bridges navigation service to UI."""

from typing import Callable, Dict, List, Optional

from nicegui import ui
from ui.services.navigation_service import NavigationService


class NavigationController:
    """Controls navigation between workspaces."""

    def __init__(self, nav_service: NavigationService):
        self._nav = nav_service
        self._nav_items: List[Dict] = []
        self._current_content: Optional[Callable] = None

    def register_workspace(self, workspace_id: str, label: str, icon: str = "tab",
                           section: str = "", disabled: bool = False) -> None:
        item = {
            "id": workspace_id,
            "label": label,
            "icon": icon,
            "section": section,
        }
        self._nav.register(item)
        self._nav_items.append(item)
        if disabled:
            self._nav.disable(workspace_id)

    def navigate(self, workspace_id: str) -> None:
        self._nav.navigate(workspace_id)

    def render_nav_item(self, item: Dict, is_active: bool, on_click: Callable) -> ui.element:
        classes = "nav-item"
        if is_active:
            classes += " active"
        if self._nav.is_disabled(item["id"]):
            classes += " disabled"

        with ui.row().classes(classes).on("click", on_click) as row:
            ui.icon(item["icon"]).classes("text-lg")
            ui.label(item["label"]).classes("text-sm")
        return row

    def render_section(self, title: str) -> None:
        ui.label(title).classes("nav-section-title")
