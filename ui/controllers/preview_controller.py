"""Preview controller — bridges preview service to UI (Sprint 4B)."""

from typing import Any, Dict, List

from ui.services.preview_service import PreviewService
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import CanonicalMetadata


class PreviewController:
    """Controls Business Preview operations from the UI."""

    def __init__(self, svc: PreviewService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def approve(self) -> None:
        if self._svc.can_approve:
            self._svc.approve()
            self._notify.success("Business preview approved. Ready for processing.")
        else:
            self._notify.warning("Cannot approve: checklist incomplete")

    def reject(self) -> None:
        self._svc.reject()
        self._notify.info("Preview rejected — returning to review")

    def reset_approval(self) -> None:
        self._svc.reset_approval()
        self._notify.info("Approval reset")

    def export_preview(self) -> str:
        data = self._svc.get_export_data()
        self._notify.success("Preview exported")
        return data

    def export_mapping(self) -> str:
        data = self._svc.get_mapping_export()
        self._notify.success("Mapping exported")
        return data

    @property
    def pipeline_stages(self) -> List[Dict[str, Any]]:
        return self._svc.pipeline_stages

    @property
    def current_stage_index(self) -> int:
        return self._svc.current_stage_index

    def get_comparison_rows(self) -> List[Dict[str, Any]]:
        return self._svc.get_comparison_rows()

    @property
    def preview_columns(self) -> List[Dict[str, Any]]:
        return self._svc.preview_columns

    @property
    def preview_rows(self) -> List[Dict[str, Any]]:
        return self._svc.preview_rows

    @property
    def preview_row_count(self) -> int:
        return self._svc.preview_row_count

    def get_validation_checks(self) -> List[Dict[str, Any]]:
        return self._svc.get_validation_checks()

    @property
    def quality_metrics(self) -> Dict[str, Any]:
        return self._svc.quality_metrics

    @property
    def business_statistics(self) -> Dict[str, Any]:
        return self._svc.business_statistics

    @property
    def metadata(self) -> CanonicalMetadata:
        return self._svc.metadata

    @property
    def warnings(self) -> List[Dict[str, Any]]:
        return self._svc.warnings

    def get_approval_checklist(self) -> List[Dict[str, Any]]:
        return self._svc.get_approval_checklist()

    @property
    def can_approve(self) -> bool:
        return self._svc.can_approve

    @property
    def is_approved(self) -> bool:
        return self._svc.is_approved

    @property
    def is_rejected(self) -> bool:
        return self._svc.is_rejected
