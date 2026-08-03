"""Notification banner widgets."""

from typing import Any, Dict

from nicegui import ui


def notification_banner(entry: Dict[str, Any]) -> ui.html:
    ntype = entry.get("type_value", "info")
    message = entry.get("message", "")
    return ui.html(
        f'<div class="notification-banner {ntype}">'
        f'<span>{message}</span>'
        f'</div>'
    )


def notification_container() -> ui.column:
    return ui.column().classes("w-full gap-1 px-2")


def show_notification(message: str, ntype: str = "info", duration: int = 5) -> None:
    color_map = {"success": "positive", "warning": "warning", "error": "negative", "info": "info"}
    ui.notify(message, type=color_map.get(ntype, "info"), timeout=duration * 1000)
