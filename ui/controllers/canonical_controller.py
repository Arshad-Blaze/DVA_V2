"""Canonical controller — bridges canonical service to UI."""

from typing import Any, Callable, Dict, List, Optional

from ui.services.canonical_service import CanonicalService
from ui.services.notification_service import NotificationService
from dav_platform.core.contracts import CanonicalMetadata


class CanonicalController:
    """Controls canonical mapping operations from the UI."""

    def __init__(self, svc: CanonicalService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    def auto_map(self) -> None:
        self._svc.auto_map()
        self._notify.success("Auto-mapping complete")

    def set_mapping(self, business_field: str, physical_column: str) -> None:
        if physical_column:
            self._svc.set_mapping(business_field, physical_column)
            self._notify.info(f"Mapped {business_field} → {physical_column}")
        else:
            self._svc.clear_mapping(business_field)
            self._notify.info(f"Cleared mapping for {business_field}")

    def clear_mapping(self, business_field: str) -> None:
        self._svc.clear_mapping(business_field)
        self._notify.info(f"Cleared mapping for {business_field}")

    def clear_all(self) -> None:
        self._svc.clear_all_mappings()
        self._notify.warning("All mappings cleared")

    def ignore_column(self, column_name: str) -> None:
        self._svc.ignore_physical(column_name)
        self._notify.info(f"Ignored column: {column_name}")

    def unignore_column(self, column_name: str) -> None:
        self._svc.unignore_physical(column_name)
        self._notify.info(f"Unignored column: {column_name}")

    def set_quantity(self, strategy: str) -> None:
        self._svc.set_quantity_strategy(strategy)
        self._notify.info(f"Quantity strategy: {strategy}")

    def set_uom(self, value: str) -> None:
        self._svc.set_uom(value)
        self._notify.info(f"UOM set to: {value}")

    def accept(self) -> None:
        missing = self._svc.get_required_missing()
        if missing:
            self._notify.warning(f"Required fields missing: {', '.join(missing)}")
            return
        self._svc.accept()
        self._notify.success("Mapping accepted")

    @property
    def metadata(self) -> CanonicalMetadata:
        return self._svc.get_metadata()

    @property
    def mappings(self) -> Dict[str, Any]:
        return self._svc.mappings

    @property
    def physical_columns(self) -> List[Dict[str, Any]]:
        return self._svc.physical_columns

    @property
    def suggestions(self) -> List[Dict[str, Any]]:
        return self._svc.suggestions

    @property
    def summary(self) -> Dict[str, Any]:
        return self._svc.get_summary()

    @property
    def accepted(self) -> bool:
        return self._svc.accepted

    @property
    def has_changes(self) -> bool:
        return self._svc.has_changes

    def get_unmapped_physical(self) -> List[str]:
        return self._svc.get_unmapped_physical()

    def get_required_missing(self) -> List[str]:
        return self._svc.get_required_missing()

    def get_business_schema(self) -> Dict[str, str]:
        return self._svc.get_business_schema_fields()
