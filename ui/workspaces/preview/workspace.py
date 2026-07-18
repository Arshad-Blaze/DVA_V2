"""Business Preview workspace — Sprint 4B.

Read-only review and approval of the canonical transformation
before proceeding to Requirement/Processing.
"""

from nicegui import ui
from ui.widgets.cards import section_header, metric_card, empty_state
from ui.shared import preview_svc, preview_ctrl
from ui.workspaces.canonical.workspace import navigate_canonical

from ui.widgets.preview.pipeline_widget import render_pipeline
from ui.widgets.preview.comparison_viewer import render_comparison
from ui.widgets.preview.canonical_table import render_canonical_table
from ui.widgets.preview.validation_card import render_validation_checks
from ui.widgets.preview.quality_dashboard import render_quality_dashboard
from ui.widgets.preview.warning_panel import render_warnings
from ui.widgets.preview.approval_card import render_approval_panel


# Forward reference for app navigation
_on_navigate = None


def set_navigation_handler(handler):
    global _on_navigate
    _on_navigate = handler


def render():
    ctrl = preview_ctrl()
    svc = preview_svc()

    # ── Pipeline ──────────────────────────────────────────────
    render_pipeline(ctrl.pipeline_stages, ctrl.current_stage_index)

    # ── Side-by-Side Comparison ───────────────────────────────
    render_comparison(ctrl.get_comparison_rows())

    # ── Business Dataset Preview ──────────────────────────────
    render_canonical_table(ctrl.preview_columns, ctrl.preview_rows, ctrl.preview_row_count)

    # ── Mapping Validation ────────────────────────────────────
    render_validation_checks(ctrl.get_validation_checks())

    # ── Transformation Quality ────────────────────────────────
    render_quality_dashboard(ctrl.quality_metrics)

    # ── Business Statistics ───────────────────────────────────
    _render_business_statistics(ctrl.business_statistics)

    # ── Metadata Explorer ─────────────────────────────────────
    _render_metadata_explorer()

    # ── Warnings ──────────────────────────────────────────────
    render_warnings(ctrl.warnings)

    # ── Approval Panel ────────────────────────────────────────
    render_approval_panel(
        checklist=ctrl.get_approval_checklist(),
        can_approve=ctrl.can_approve,
        is_approved=ctrl.is_approved,
        is_rejected=ctrl.is_rejected,
        on_approve=ctrl.approve,
        on_reject=ctrl.reject,
        on_back=navigate_canonical,
    )


# ── Section: Business Statistics ───────────────────────────────

def _render_business_statistics(stats):
    section_header("Business Statistics")
    if not stats:
        empty_state("No statistics available")
        return
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            metric_card("Total Rows", f"{stats.get('total_rows', 0):,}", "table_rows", "blue")
            metric_card("Columns", str(stats.get("total_columns", 0)), "view_column", "blue")
            metric_card("Stores", str(stats.get("stores", 0)), "store", "green")
            metric_card("Unique UPCs", f"{stats.get('unique_upcs', 0):,}", "barcode", "green")
        with ui.grid(columns=4).classes("w-full gap-4 mt-2"):
            metric_card("Categories", str(stats.get("categories", 0)), "category", "orange")
            metric_card("Brands", str(stats.get("brands", 0)), "branding_watermark", "orange")
            metric_card("Departments", str(stats.get("departments", 0)), "business", "orange")
            metric_card("Date Range", stats.get("date_range", "-"), "calendar_month", "blue")
        with ui.grid(columns=3).classes("w-full gap-4 mt-2"):
            metric_card("Null %", f"{stats.get('null_pct', 0):.1f}%", "priority_high",
                        "red" if stats.get("null_pct", 0) > 5 else "grey")
            metric_card("Duplicate %", f"{stats.get('duplicate_pct', 0):.1f}%", "content_copy",
                        "red" if stats.get("duplicate_pct", 0) > 2 else "grey")
            metric_card("Completeness", f"{stats.get('completeness', 0):.1f}%", "check_circle",
                        "green" if stats.get("completeness", 100) > 95 else "orange")


# ── Section: Metadata Explorer ─────────────────────────────────

def _render_metadata_explorer():
    from ui.widgets.preview.metadata_card import render_metadata_explorer as _render_meta
    _render_meta(preview_ctrl().metadata)
