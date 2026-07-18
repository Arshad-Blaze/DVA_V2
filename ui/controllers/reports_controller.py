"""Reports controller — bridges reports service to UI (Sprint 8)."""

from typing import Any, Dict, List, Optional
from ui.services.reports_service import ReportsService
from ui.services.notification_service import NotificationService


class ReportsController:
    """Controls Reports & Insights Center operations from the UI."""

    def __init__(self, svc: ReportsService, notify: NotificationService):
        self._svc = svc
        self._notify = notify

    # ── Executive Dashboard ───────────────────────────────────

    @property
    def executive_dashboard(self) -> Dict[str, Any]:
        return self._svc.executive_dashboard

    # ── Business KPIs ─────────────────────────────────────────

    @property
    def business_kpis(self) -> Dict[str, Any]:
        return self._svc.business_kpis

    # ── Validation KPIs ───────────────────────────────────────

    @property
    def validation_kpis(self) -> Dict[str, Any]:
        return self._svc.validation_kpis

    # ── Report Explorer ───────────────────────────────────────

    @property
    def report_explorer(self) -> Dict[str, Any]:
        return self._svc.report_explorer

    @property
    def filtered_reports(self) -> List[Dict[str, Any]]:
        return self._svc.filtered_reports

    @property
    def report_count(self) -> int:
        return self._svc.report_count

    def set_search_query(self, query: str) -> None:
        self._svc.set_search_query(query)

    def select_category(self, category: Optional[str]) -> None:
        self._svc.select_category(category)

    def select_report(self, report_id: str) -> None:
        self._svc.select_report(report_id)

    @property
    def selected_report(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_report

    # ── Interactive Reports ───────────────────────────────────

    @property
    def all_reports(self) -> List[Dict[str, Any]]:
        return self._svc.all_reports

    # ── Charts ────────────────────────────────────────────────

    @property
    def chart_data(self) -> Dict[str, Any]:
        return self._svc.chart_data

    @property
    def chart_keys(self) -> List[str]:
        return self._svc.chart_keys

    def select_chart(self, chart_key: Optional[str]) -> None:
        self._svc.select_chart(chart_key)

    @property
    def selected_chart(self) -> Optional[Dict[str, Any]]:
        return self._svc.selected_chart

    @property
    def selected_chart_key(self) -> Optional[str]:
        return getattr(self._svc, '_selected_chart', None)

    # ── Drill Down ────────────────────────────────────────────

    @property
    def drill_down_level(self) -> str:
        return self._svc.drill_down_level

    @property
    def drill_down_id(self) -> Optional[str]:
        return self._svc.drill_down_id

    @property
    def drill_down_data(self) -> Dict[str, Any]:
        return self._svc.drill_down_data

    def drill_to_store(self, store_id: str) -> None:
        self._svc.drill_to_store(store_id)
        self._notify.info(f"Drilled down to store {store_id}")

    def drill_to_upc(self, upc_id: str) -> None:
        self._svc.drill_to_upc(upc_id)
        self._notify.info(f"Drilled down to UPC {upc_id}")

    def drill_to_validation(self) -> None:
        self._svc.drill_to_validation()
        self._notify.info("Drilled to validation details")

    def drill_to_business(self) -> None:
        self._svc.drill_to_business()
        self._notify.info("Drilled to business details")

    def drill_up(self) -> None:
        self._svc.drill_up()
        self._notify.info("Drilled up")

    def drill_reset(self) -> None:
        self._svc.drill_reset()
        self._notify.info("Reset drill-down to dashboard level")

    # ── Export Center ─────────────────────────────────────────

    @property
    def export_formats(self) -> List[str]:
        return self._svc.export_formats

    @property
    def selected_format(self) -> str:
        return self._svc.selected_format

    def select_format(self, fmt: str) -> None:
        self._svc.select_format(fmt)

    def preview_export(self) -> str:
        return self._svc.preview_export()

    def export_report(self) -> str:
        data = self._svc.export_report()
        self._notify.success("Report exported")
        return data

    def export_all(self) -> str:
        data = self._svc.export_all()
        self._notify.success("All reports exported")
        return data

    # ── Report History ────────────────────────────────────────

    @property
    def report_history(self) -> List[Dict[str, Any]]:
        return self._svc.report_history

    # ── Status Bar ────────────────────────────────────────────

    @property
    def status_bar(self) -> Dict[str, Any]:
        return self._svc.status_bar
