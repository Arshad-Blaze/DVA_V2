"""Tests for Validation Center (Sprint 7)."""

from unittest.mock import MagicMock
import pytest

from ui.services.validation_service import ValidationService
from ui.controllers.validation_controller import ValidationController
from ui.shared import WorkspaceContext


@pytest.fixture
def ctx():
    return WorkspaceContext()


@pytest.fixture
def svc(ctx):
    return ValidationService(ctx)


@pytest.fixture
def notify():
    return MagicMock()


@pytest.fixture
def ctrl(svc, notify):
    return ValidationController(svc, notify)


class TestValidationService:

    def test_dashboard_metrics(self, svc):
        d = svc.dashboard
        assert "total_rules" in d
        assert d["total_rules"] == 20

    def test_heat_map_rows(self, svc):
        assert len(svc.heat_map_rows) == 5

    def test_heat_map_columns(self, svc):
        assert len(svc.heat_map_columns) == 7

    def test_heat_map_data(self, svc):
        data = svc.heat_map_data
        assert len(data) == 5

    def test_get_heat_map_cell(self, svc):
        assert svc.get_heat_map_cell("S001", "Store") == "pass"

    def test_all_issues_default(self, svc):
        assert len(svc.all_issues) == 4

    def test_all_issues_have_severity(self, svc):
        for issue in svc.all_issues:
            assert issue["severity"] in ("error", "warning", "info")

    def test_all_issues_have_recommendation(self, svc):
        for issue in svc.all_issues:
            assert "recommendation" in issue

    def test_filter_by_severity(self, svc):
        svc.set_severity_filter("error")
        assert all(i["severity"] == "error" for i in svc.filtered_issues)

    def test_filter_by_search(self, svc):
        svc.set_search_query("price")
        assert len(svc.filtered_issues) > 0
        svc.set_search_query("")

    def test_issue_count(self, svc):
        assert svc.issue_count > 0

    def test_select_issue(self, svc):
        svc.select_issue(0)
        assert svc.selected_issue is not None

    def test_comparison_data(self, svc):
        cmp = svc.comparison_data
        assert len(cmp) == 7
        for item in cmp:
            assert "metric" in item
            assert "expected" in item
            assert "actual" in item

    def test_all_rules(self, svc):
        rules = svc.all_rules
        assert len(rules) == 6
        for r in rules:
            assert "name" in r
            assert "description" in r

    def test_select_rule_by_name(self, svc):
        svc.select_rule("store_sales_not_zero")
        assert svc.selected_rule is not None
        assert svc.selected_rule["name"] == "store_sales_not_zero"

    def test_business_impact(self, svc):
        b = svc.business_impact
        assert "business_readiness" in b
        assert "risk_level" in b

    def test_suggested_actions(self, svc):
        actions = svc.suggested_actions
        assert len(actions) == 4
        for a in actions:
            assert "action" in a
            assert "reason" in a

    def test_timeline_stages(self, svc):
        stages = svc.timeline_stages
        assert len(stages) == 6
        for s in stages:
            assert "id" in s
            assert "label" in s

    def test_approve(self, svc):
        svc.approve()
        assert svc.is_approved is True
        assert svc.is_rejected is False

    def test_reject(self, svc):
        svc.reject()
        assert svc.is_rejected is True
        assert svc.is_approved is False

    def test_reset(self, svc):
        svc.approve()
        svc.reset()
        assert svc.is_approved is False
        assert svc.is_rejected is False

    def test_export_report(self, svc):
        data = svc.export_report()
        assert isinstance(data, str)
        assert "Rule" in data

    def test_export_failed(self, svc):
        data = svc.export_failed_records()
        assert isinstance(data, str)
        assert "Rule" in data

    def test_on_change_callback(self, svc):
        cb = MagicMock()
        svc.on_change(cb)
        svc.approve()
        cb.assert_called_once()


class TestValidationController:

    def test_properties_delegate(self, ctrl, svc):
        assert ctrl.dashboard == svc.dashboard

    def test_heat_map_delegation(self, ctrl, svc):
        assert ctrl.heat_map_rows == svc.heat_map_rows
        assert ctrl.heat_map_columns == svc.heat_map_columns

    def test_filtered_issues_delegates(self, ctrl, svc):
        assert ctrl.filtered_issues == svc.filtered_issues

    def test_set_search_query_delegates(self, ctrl, svc):
        ctrl.set_search_query("test")
        assert svc._search_query == "test"

    def test_set_severity_filter_delegates(self, ctrl, svc):
        ctrl.set_severity_filter("low")
        assert svc._filter_severity == "low"

    def test_select_issue_delegates(self, ctrl, svc):
        ctrl.select_issue(1)
        assert svc._selected_issue == 1

    def test_comparison_data_delegates(self, ctrl, svc):
        assert ctrl.comparison_data == svc.comparison_data

    def test_all_rules_delegates(self, ctrl, svc):
        assert ctrl.all_rules == svc.all_rules

    def test_select_rule_delegates(self, ctrl, svc):
        ctrl.select_rule("store_sales_not_zero")
        assert ctrl.selected_rule == svc.selected_rule

    def test_business_impact_delegates(self, ctrl, svc):
        assert ctrl.business_impact == svc.business_impact

    def test_suggested_actions_delegates(self, ctrl, svc):
        assert ctrl.suggested_actions == svc.suggested_actions

    def test_timeline_stages_delegates(self, ctrl, svc):
        assert ctrl.timeline_stages == svc.timeline_stages

    def test_is_approved_delegates(self, ctrl, svc):
        assert ctrl.is_approved == svc.is_approved

    def test_is_rejected_delegates(self, ctrl, svc):
        assert ctrl.is_rejected == svc.is_rejected

    def test_approve_notifies(self, ctrl, notify):
        ctrl.approve()
        notify.success.assert_called_once()

    def test_reject_notifies(self, ctrl, notify):
        ctrl.reject()
        notify.warning.assert_called_once()

    def test_reset_notifies(self, ctrl, notify):
        ctrl.reset()
        notify.info.assert_called_once()

    def test_export_report(self, ctrl, svc):
        assert ctrl.export_report() == svc.export_report()

    def test_export_failed(self, ctrl, svc):
        assert ctrl.export_failed() == svc.export_failed_records()


class TestValidationBackendWiring:
    def test_validate_runs_backend_engine(self, ctx):
        import polars as pl
        from dav_platform.core.contracts import ProcessingResult, ValidationSeverity

        svc = ValidationService(ctx)
        assert svc.has_result is False

        df = pl.DataFrame({"store": ["S1", "S1", "S2"], "quantity": [1, -2, 3]})
        result = ProcessingResult(df=df, row_count=3, errors=[])
        vr = svc.validate(result)

        assert svc.has_result is True
        assert vr is svc._result or vr.passed is not None
        d = svc.dashboard
        assert "total_rules" in d
        assert d["overall_quality"] in ("High", "Low")
        assert d["business_readiness"] in ("Good", "Needs Review")

    def test_load_result_injects_issues(self, ctx):
        from dav_platform.core.contracts import (
            ProcessingResult,
            ValidationIssue,
            ValidationResult,
            ValidationSeverity,
        )

        df = None
        vr = ValidationResult(
            passed=False,
            issues=[
                ValidationIssue(
                    rule="price_non_negative",
                    message="UPC has negative price",
                    severity=ValidationSeverity.ERROR,
                    row_count=3,
                    column="price",
                ),
            ],
            error_count=1,
            warning_count=0,
        )
        svc = ValidationService(ctx)
        svc.load_result(vr)

        assert svc.has_result is True
        issues = svc.all_issues
        assert len(issues) == 1
        assert issues[0]["rule"] == "price_non_negative"
        assert issues[0]["severity"] == "error"
        assert issues[0]["affected_records"] == 3
        assert svc.dashboard["failed"] == 1
