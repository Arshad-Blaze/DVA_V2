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


class NotificationService:
    """Manages UI notifications with type, message, and duration."""

    def __init__(self):
        self._notifications: List[Dict[str, Any]] = []
        self._on_notify: Optional[Callable] = None

    def notify(self, message: str, ntype: NotificationType = NotificationType.INFO, duration: int = 5) -> None:
        entry = {
            "message": message,
            "type": ntype,
            "type_value": ntype.value,
            "color": _notification_colors.get(ntype, "#2196f3"),
            "duration": duration,
        }
        self._notifications.append(entry)
        if self._on_notify:
            self._on_notify(entry)

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
