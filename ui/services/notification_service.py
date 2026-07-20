from enum import Enum
from typing import Any, Dict, List, Optional, Callable


class NotificationType(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    PROGRESS = "progress"


_notification_colors = {
    NotificationType.SUCCESS: "#4caf50",
    NotificationType.WARNING: "#ff9800",
    NotificationType.ERROR: "#f44336",
    NotificationType.INFO: "#2196f3",
    NotificationType.PROGRESS: "#9c27b0",
}

_notification_icons = {
    NotificationType.SUCCESS: "check_circle",
    NotificationType.WARNING: "warning",
    NotificationType.ERROR: "error",
    NotificationType.INFO: "info",
    NotificationType.PROGRESS: "hourglass_top",
}


class NotificationService:
    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        self._on_notify: Optional[Callable] = None

    def notify(self, message: str, ntype: NotificationType = NotificationType.INFO, duration: int = 5) -> None:
        entry = {
            "message": message,
            "type": ntype,
            "type_value": ntype.value,
            "color": _notification_colors.get(ntype, "#2196f3"),
            "icon": _notification_icons.get(ntype, "info"),
            "duration": duration,
        }
        self._notifications.append(entry)
        if self._on_notify:
            self._on_notify(entry)
        self._schedule_dismiss(entry, duration)

    def _schedule_dismiss(self, entry: Dict[str, Any], duration: int) -> None:
        if duration > 0:
            from nicegui import ui
            ui.timer(duration, lambda e=entry: self.dismiss(e), once=True)

    def dismiss(self, entry: Dict[str, Any]) -> None:
        if entry in self._notifications:
            self._notifications.remove(entry)

    def success(self, message: str, duration: int = 5) -> None:
        self.notify(message, NotificationType.SUCCESS, duration)

    def warning(self, message: str, duration: int = 7) -> None:
        self.notify(message, NotificationType.WARNING, duration)

    def error(self, message: str, duration: int = 10) -> None:
        self.notify(message, NotificationType.ERROR, duration)

    def info(self, message: str, duration: int = 5) -> None:
        self.notify(message, NotificationType.INFO, duration)

    def progress(self, message: str, duration: int = 0) -> None:
        self.notify(message, NotificationType.PROGRESS, duration)

    def on_notification(self, callback: Callable) -> None:
        self._on_notify = callback

    @property
    def notifications(self) -> List[Dict[str, Any]]:
        return list(self._notifications)

    def clear(self) -> None:
        self._notifications.clear()
