"""Tests for Reports & Insights Center (Sprint 8)."""

from unittest.mock import MagicMock
import pytest

from ui.services.reports_service import ReportsService
from ui.controllers.reports_controller import ReportsController
from ui.shared import WorkspaceContext


@pytest.fixture
def ctx():
    return WorkspaceContext()


@pytest.fixture
def svc(ctx):
    return ReportsService(ctx)


@pytest.fixture
def notify():
    return MagicMock()


@pytest.fixture
def ctrl(svc, notify):
    return ReportsController(svc, notify)


class TestReportsService:

    # ── Executive Dashboard ──────────────────────────────────

    def test_executive_dashboard_keys(self, svc):
        d = svc.executive_dashboard
        assert d["overall_health"] == "Good"
        assert "validation_score" in d
        assert "reports_generated" in d

    # ── Business KPIs ────────────────────────────────────────

    def test_business_kpis_keys(self, svc):
        k = svc.business_kpis
        assert "stores" in k
        assert "total_sales" in k
        assert "date_range" in k

    def test_business_kpis_store_coverage(self, svc):
        k = svc.business_kpis
        assert k["stores"]["coverage_pct"] == 90.0

    # ── Validation KPIs ──────────────────────────────────────

    def test_validation_kpis_keys(self, svc):
        k = svc.validation_kpis
        assert k["passed_rules"] == 16
        assert k["failed_rules"] == 2

    # ── Report Explorer ──────────────────────────────────────

    def test_report_explorer_categories(self, svc):
        e = svc.report_explorer
        assert len(e["categories"]) == 4

    def test_report_explorer_pinned(self, svc):
        e = svc.report_explorer
        assert len(e["pinned"]) == 2

    def test_report_explorer_recent(self, svc):
        e = svc.report_explorer
        assert len(e["recent"]) == 3

    def test_filtered_reports_default(self, svc):
        assert len(svc.filtered_reports) == 10

    def test_filtered_reports_by_category(self, svc):
        svc.select_category("store")
        filtered = svc.filtered_reports
        assert all(r["type"] == "Store" for r in filtered)

    def test_filtered_reports_by_search(self, svc):
        svc.set_search_query("Executive")
        filtered = svc.filtered_reports
        assert len(filtered) > 0
        svc.set_search_query("")

    def test_report_count(self, svc):
        assert svc.report_count == 10

    def test_select_report(self, svc):
        svc.select_report("r1")
        r = svc.selected_report
        assert r is not None
        assert r["id"] == "r1"

    def test_select_nonexistent_report(self, svc):
        svc.select_report("nonexistent")
        assert svc.selected_report is None

    # ── Charts ───────────────────────────────────────────────

    def test_chart_keys(self, svc):
        keys = svc.chart_keys
        assert len(keys) == 6

    def test_chart_data_shape(self, svc):
        data = svc.chart_data
        for key in svc.chart_keys:
            assert "labels" in data[key]
            assert "values" in data[key]

    def test_select_chart(self, svc):
        svc.select_chart("sales_by_store")
        chart = svc.selected_chart
        assert chart is not None
        assert "labels" in chart

    def test_select_chart_none(self, svc):
        svc.select_chart(None)
        assert svc.selected_chart is None

    # ── Drill Down ───────────────────────────────────────────

    def test_drill_down_level_default(self, svc):
        assert svc.drill_down_level == "dashboard"

    def test_drill_to_store(self, svc):
        svc.drill_to_store("S001")
        assert svc.drill_down_level == "store"
        assert svc.drill_down_id == "S001"

    def test_drill_to_upc(self, svc):
        svc.drill_to_upc("490123456001")
        assert svc.drill_down_level == "upc"

    def test_drill_to_validation(self, svc):
        svc.drill_to_validation()
        assert svc.drill_down_level == "validation"

    def test_drill_to_business(self, svc):
        svc.drill_to_business()
        assert svc.drill_down_level == "business"

    def test_drill_up(self, svc):
        svc.drill_to_store("S001")
        svc.drill_up()
        assert svc.drill_down_level == "dashboard"

    def test_drill_reset(self, svc):
        svc.drill_to_store("S001")
        svc.drill_reset()
        assert svc.drill_down_level == "dashboard"

    def test_drill_down_data(self, svc):
        data = svc.drill_down_data
        assert "stores" in data
        assert len(data["stores"]) == 5

    # ── Export Center ────────────────────────────────────────

    def test_export_formats(self, svc):
        assert len(svc.export_formats) == 5

    def test_select_format(self, svc):
        svc.select_format("pdf")
        assert svc.selected_format == "pdf"

    def test_preview_export_csv(self, svc):
        svc.select_report("r1")
        svc.select_format("csv")
        preview = svc.preview_export()
        assert "Executive Summary" in preview

    def test_preview_export_json(self, svc):
        svc.select_report("r2")
        svc.select_format("json")
        preview = svc.preview_export()
        assert "Store Summary" in preview

    def test_export_report(self, svc):
        svc.select_report("r1")
        data = svc.export_report()
        assert len(data) > 0

    def test_export_all(self, svc):
        data = svc.export_all()
        assert len(data) > 0

    def test_export_all_json(self, svc):
        svc.select_format("json")
        data = svc.export_all("json")
        assert "[" in data

    # ── Report History ───────────────────────────────────────

    def test_report_history(self, svc):
        h = svc.report_history
        assert len(h) == 4
        for entry in h:
            assert "execution_id" in entry
            assert "status" in entry

    # ── Status Bar ───────────────────────────────────────────

    def test_status_bar_default(self, svc):
        s = svc.status_bar
        assert s["report_count"] == 10
        assert s["current_report"] is None

    def test_status_bar_with_selection(self, svc):
        svc.select_report("r1")
        s = svc.status_bar
        assert s["current_report"] == "Executive Summary"

    # ── Events ───────────────────────────────────────────────

    def test_on_change_callback(self, svc):
        cb = MagicMock()
        svc.on_change(cb)
        svc.select_report("r1")
        cb.assert_called_once()


class TestReportsController:

    def test_executive_dashboard_delegates(self, ctrl, svc):
        assert ctrl.executive_dashboard == svc.executive_dashboard

    def test_business_kpis_delegates(self, ctrl, svc):
        assert ctrl.business_kpis == svc.business_kpis

    def test_validation_kpis_delegates(self, ctrl, svc):
        assert ctrl.validation_kpis == svc.validation_kpis

    def test_report_explorer_delegates(self, ctrl, svc):
        assert ctrl.report_explorer == svc.report_explorer

    def test_filtered_reports_delegates(self, ctrl, svc):
        assert ctrl.filtered_reports == svc.filtered_reports

    def test_select_report_delegates(self, ctrl, svc):
        ctrl.select_report("r1")
        assert svc.selected_report is not None

    def test_chart_keys_delegates(self, ctrl, svc):
        assert ctrl.chart_keys == svc.chart_keys

    def test_select_chart_delegates(self, ctrl, svc):
        ctrl.select_chart("sales_by_store")
        assert ctrl.selected_chart == svc.selected_chart

    def test_selected_chart_key(self, ctrl):
        ctrl.select_chart("sales_by_store")
        assert ctrl.selected_chart_key == "sales_by_store"

    def test_drill_down_level_delegates(self, ctrl, svc):
        assert ctrl.drill_down_level == svc.drill_down_level

    def test_drill_to_store_notifies(self, ctrl, notify):
        ctrl.drill_to_store("S001")
        notify.info.assert_called_once()

    def test_drill_to_upc_notifies(self, ctrl, notify):
        ctrl.drill_to_upc("U001")
        notify.info.assert_called_once()

    def test_drill_to_validation_notifies(self, ctrl, notify):
        ctrl.drill_to_validation()
        notify.info.assert_called_once()

    def test_drill_to_business_notifies(self, ctrl, notify):
        ctrl.drill_to_business()
        notify.info.assert_called_once()

    def test_drill_up_notifies(self, ctrl, notify):
        ctrl.drill_up()
        notify.info.assert_called_once()

    def test_drill_reset_notifies(self, ctrl, notify):
        ctrl.drill_reset()
        notify.info.assert_called_once()

    def test_export_formats_delegates(self, ctrl, svc):
        assert ctrl.export_formats == svc.export_formats

    def test_select_format_delegates(self, ctrl, svc):
        ctrl.select_format("pdf")
        assert svc.selected_format == "pdf"

    def test_preview_export(self, ctrl, svc):
        svc.select_report("r1")
        assert ctrl.preview_export() == svc.preview_export()

    def test_export_report_notifies(self, ctrl, notify):
        ctrl.select_report("r1")
        ctrl.export_report()
        notify.success.assert_called_once()

    def test_export_all_notifies(self, ctrl, notify):
        ctrl.export_all()
        notify.success.assert_called_once()

    def test_report_history_delegates(self, ctrl, svc):
        assert ctrl.report_history == svc.report_history

    def test_status_bar_delegates(self, ctrl, svc):
        assert ctrl.status_bar == svc.status_bar
