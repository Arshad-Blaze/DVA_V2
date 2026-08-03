"""Detection controller — bridges detection service to UI."""

from typing import Any, Dict, List, Optional

from ui.services.detection_service import DetectionService
from ui.services.notification_service import NotificationService


class DetectionController:
    """Controls detection operations from the UI."""

    def __init__(self, detection_svc: DetectionService, notify_svc: NotificationService):
        self._svc = detection_svc
        self._notify = notify_svc

    def run_detection(self, file_path: Optional[str] = None) -> None:
        self._svc.run_detection(file_path)
        self._notify.info("Detection complete")

    def validate_detection(self) -> bool:
        ok = self._svc.validate_detection()
        if ok:
            self._notify.success("Detection validated successfully")
        else:
            self._notify.warning("Validation found issues")
        return ok

    def accept_detection(self) -> None:
        self._svc.accept_detection()
        self._notify.success("Detection accepted")

    def switch_file(self, file_name: str) -> None:
        self._svc.switch_file(file_name)
        self._notify.info(f"Switched to {file_name}")

    def set_override(self, key: str, value: Any) -> None:
        self._svc.set_override(key, value)
        self._notify.info(f"Override set: {key} = {value}")

    def clear_override(self, key: str) -> None:
        self._svc.clear_override(key)
        self._notify.info(f"Override cleared: {key}")

    def clear_all_overrides(self) -> None:
        self._svc.clear_all_overrides()
        self._notify.info("All overrides cleared")

    @property
    def result(self):
        return self._svc.result

    @property
    def timeline(self) -> List[Dict[str, Any]]:
        return self._svc.timeline

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return self._svc.warnings

    @property
    def status(self) -> str:
        return self._svc.detection_status

    @property
    def selected_file(self) -> Optional[str]:
        return self._svc.selected_file

    @property
    def selected_files(self) -> List[str]:
        return self._svc.selected_files

    @property
    def is_accepted(self) -> bool:
        return self._svc.is_accepted

    @property
    def has_overrides(self) -> bool:
        return self._svc.has_overrides

    def get_effective_value(self, key: str, detected: Any) -> Any:
        return self._svc.get_effective_value(key, detected)

    def get_summary(self) -> Dict[str, Any]:
        return self._svc.get_detection_summary()
