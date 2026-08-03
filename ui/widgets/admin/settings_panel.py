"""Settings panel widget (Sprint 9)."""

from typing import Any, Callable, Dict
from nicegui import ui
from ui.widgets.cards import section_header


SECTION_LABELS = {
    "application": "Application",
    "theme": "Theme",
    "workspace": "Workspace",
    "preferences": "Preferences",
    "reports": "Reports",
    "notifications": "Notifications",
    "shortcuts": "Shortcuts",
}


def render_settings_panel(
    settings: Dict[str, Any],
    defaults: Dict[str, Any],
    on_update: Callable,
    on_reset: Callable,
) -> None:
    section_header("Settings")
    with ui.card().classes("w-full p-4"):
        with ui.tabs().classes("w-full") as tabs:
            section_keys = ["application", "theme", "workspace", "preferences", "reports", "notifications", "shortcuts"]
            for key in section_keys:
                ui.tab(SECTION_LABELS.get(key, key.title()), icon="settings" if key == "application" else None)

        with ui.tab_panels(tabs, value=section_keys[0]).classes("w-full"):
            for key in section_keys:
                label = SECTION_LABELS.get(key, key.title())
                with ui.tab_panel(label):
                    section = settings.get(key, {})
                    default_section = defaults.get(key, {})
                    for prop_key, value in section.items():
                        default_val = default_section.get(prop_key)
                        is_changed = value != default_val
                        with ui.row().classes("w-full items-center gap-3 py-1"):
                            ui.label(prop_key.replace("_", " ").title()).classes("text-sm w-40")
                            if isinstance(value, bool):
                                ui.switch(value=value, on_change=lambda v, s=key, k=prop_key: on_update(s, k, v.value)
                                          ).props("dense" + (" color=primary" if is_changed else ""))
                            elif isinstance(value, (int, float)):
                                ui.input(value=str(value),
                                         on_change=lambda e, s=key, k=prop_key: on_update(s, k, type(section[k])(e.value) if e.value else section[k])
                                         ).props("outlined dense").classes("w-32")
                            else:
                                ui.input(value=str(value),
                                         on_change=lambda e, s=key, k=prop_key: on_update(s, k, e.value)
                                         ).props("outlined dense").classes("w-48")
                            if is_changed:
                                ui.icon("edit", color="orange", size="sm")
        with ui.row().classes("gap-2 mt-3"):
            ui.button("Reset to Defaults", icon="restart_alt", on_click=on_reset).props("flat")
