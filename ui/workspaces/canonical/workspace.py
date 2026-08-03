"""Canonical workspace — Canonical Mapping Studio.

Sprint 4A: Column mapping, business schema builder, quantity/UOM resolution.
"""

from typing import List

from nicegui import ui
from ui.widgets.cards import section_header, status_badge
from ui.shared import canonical_svc, canonical_ctrl, detection_svc, navigate_to
from ui.widgets.guidance_bar import render_guidance

# ──────────────────────────────────────────────────────────────────
# Section 1 — Detection Summary
# ──────────────────────────────────────────────────────────────────

def _render_detection_summary():
    section_header("Detection Summary")
    det_svc = detection_svc()
    r = det_svc.result
    with ui.card().classes("w-full p-4"):
        with ui.grid(columns=4).classes("w-full gap-4"):
            if r:
                _summary_item("Format", r.file_type.value.title() if r.file_type else "Unknown")
                _summary_item("Delimiter", f"Comma '{r.delimiter}'" if r.delimiter else "None")
                _summary_item("Encoding", r.encoding.upper())
                _summary_item("Header", f"Row {r.header_start_line + 1}" if r.has_header else "None")
                _summary_item("Record Types", "Single-line" if not r.is_multiline else "Multi-line")
                _summary_item("Layout", f"{len(r.columns or [])} columns")
                _summary_item("Confidence", f"{r.confidence * 100:.0f}%")
                _summary_item("Accepted", "Yes" if det_svc.is_accepted else "No")
            else:
                _summary_item("Format", "—")
                _summary_item("Delimiter", "—")
                _summary_item("Encoding", "—")
                _summary_item("Header", "—")
                _summary_item("Record Types", "—")
                _summary_item("Layout", "—")
                _summary_item("Confidence", "—")
                _summary_item("Accepted", "—")

# ──────────────────────────────────────────────────────────────────
# Section 2 — Physical Schema Explorer
# ──────────────────────────────────────────────────────────────────

def _render_physical_schema():
    section_header("Physical Schema Explorer")
    svc = canonical_svc()
    cols = svc.physical_columns

    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between mb-3"):
            ui.label(f"{len(cols)} columns detected").classes("text-sm text-gray-500")
            ui.input(placeholder="Search columns...").classes("min-w-40").props("dense outlined")

        with ui.table(rows=cols, row_key="name", columns=[
            {"name": "name", "label": "Column", "field": "name", "align": "left"},
            {"name": "sample", "label": "Sample Values", "field": "sample", "align": "left"},
            {"name": "type", "label": "Type", "field": "type", "align": "center"},
            {"name": "null_pct", "label": "Null %", "field": "null_pct", "align": "center"},
            {"name": "conf", "label": "Confidence", "field": "conf", "align": "center"},
        ]).classes("w-full"):
            pass

        for c in cols:
            ignored = c["name"] in svc.ignored_physical
            opacity = "opacity-40" if ignored else ""
            with ui.row().classes(f"items-center gap-3 py-2 px-2 {opacity}"):
                ui.label(c["name"]).classes("text-sm font-mono min-w-28")
                ui.label(c["sample"]).classes("text-xs text-gray-400 flex-1")
                ui.label(c["type"]).classes("text-xs min-w-16 text-center")
                _progress_bar(c["conf"])
                if ignored:
                    ui.button(icon="visibility", on_click=lambda n=c["name"]: (
                        canonical_ctrl().unignore_column(n)
                    )).props("flat round dense size=sm").tooltip("Show column")
                else:
                    ui.button(icon="visibility_off", on_click=lambda n=c["name"]: (
                        canonical_ctrl().ignore_column(n)
                    )).props("flat round dense size=sm").tooltip("Ignore column")

# ──────────────────────────────────────────────────────────────────
# Section 3+4+5 — Business Schema Builder & Mapping Studio
# ──────────────────────────────────────────────────────────────────

def _render_business_schema():
    section_header("Business Schema Builder")
    svc = canonical_svc()
    schema = svc.get_business_schema_fields()
    physical_names = [""] + [c["name"] for c in svc.physical_columns]

    with ui.card().classes("w-full p-4"):
        ui.label("Essentials").classes("text-md font-bold text-primary")

        for field in ["store", "upc", "description", "quantity", "price", "date"]:
            _render_mapping_row(field, schema.get(field, ""), physical_names, svc)

        with ui.expansion("Advanced Fields", icon="expand_more").classes("w-full mt-3"):
            for field in ["category", "brand", "department", "price", "promotion",
                          "currency", "uom", "weight", "time", "store_name",
                          "record_type", "region", "division"]:
                _render_mapping_row(field, schema.get(field, ""), physical_names, svc)


def _render_mapping_row(field: str, purpose: str, physical_names: List[str], svc) -> None:
    mapping = svc.get_mapping(field)
    has_mapping = mapping is not None and mapping.physical_column
    current_val = mapping.physical_column if has_mapping else ""
    conf = mapping.confidence if has_mapping else 0.0
    is_auto = mapping.source == "candidate" if has_mapping else False

    with ui.row().classes("items-center gap-3 w-full py-2 border-bottom"):
        with ui.column().classes("min-w-28 gap-0"):
            ui.label(field).classes("text-sm font-semibold")
            ui.label(purpose).classes("text-xs text-gray-400")

        ui.select(
            physical_names, value=current_val, label="Physical Column",
            on_change=lambda e, f=field: canonical_ctrl().set_mapping(f, e.value),
        ).classes("min-w-40 flex-1")

        with ui.row().classes("items-center gap-2 min-w-32"):
            _progress_bar(conf)
            if is_auto and has_mapping:
                ui.label("Auto").classes("text-xs text-positive")
            elif has_mapping:
                ui.label("Manual").classes("text-xs text-warning")
            else:
                ui.label("—").classes("text-xs text-gray-400")

        if has_mapping:
            ui.button(icon="close", on_click=lambda f=field: (
                canonical_ctrl().clear_mapping(f)
            )).props("flat round dense size=sm color=negative")


# ──────────────────────────────────────────────────────────────────
# Section 6+7 — Quantity & UOM Resolution
# ──────────────────────────────────────────────────────────────────

def _render_quantity_uom():
    ui.space().classes("h-4")
    section_header("Quantity & UOM Resolution")

    svc = canonical_svc()

    with ui.grid(columns=2).classes("w-full gap-4"):
        with ui.card().classes("w-full p-4"):
            ui.label("Quantity Resolution").classes("text-sm font-bold mb-3")
            ui.label("Detected Strategy").classes("text-xs text-gray-400")
            ui.label(f"Current: {svc.quantity_strategy}").classes("text-lg font-bold mt-1")

            with ui.row().classes("items-center gap-3 mt-3"):
                ui.select(
                    ["units", "weighted_qty", "weight", "none"],
                    value=svc.quantity_strategy,
                    label="Override Strategy",
                    on_change=lambda e: canonical_ctrl().set_quantity(e.value),
                ).classes("min-w-40")

            ui.label("Weight column is preferred when available; Units is fallback.").classes("text-xs text-gray-400 mt-2")

            # Show resolved quantity
            mapping = svc.get_mapping("quantity")
            if mapping and mapping.physical_column:
                with ui.row().classes("items-center gap-2 mt-2 p-2 bg-positive-50 rounded"):
                    ui.icon("check_circle", color="positive").classes("text-sm")
                    ui.label(f"Resolved: {mapping.physical_column}").classes("text-sm font-medium")

        with ui.card().classes("w-full p-4"):
            ui.label("Unit of Measure (UOM)").classes("text-sm font-bold mb-3")
            ui.label("Detected UOM").classes("text-xs text-gray-400")
            ui.label(f"Current: {svc.uom_value}").classes("text-lg font-bold mt-1")

            with ui.row().classes("items-center gap-3 mt-3"):
                ui.select(
                    ["each", "case", "pound", "kg", "liter", "gallon", "box", "pallet"],
                    value=svc.uom_value,
                    label="Override UOM",
                    on_change=lambda e: canonical_ctrl().set_uom(e.value),
                ).classes("min-w-40")

            ui.label("UOM normalization ensures consistent measurement across all products.").classes("text-xs text-gray-400 mt-2")

            with ui.row().classes("items-center gap-2 mt-2"):
                ui.label("Sample values: each, EA, piece, unit").classes("text-xs text-gray-500")


# ──────────────────────────────────────────────────────────────────
# Section 8 — Mapping Confidence Dashboard
# ──────────────────────────────────────────────────────────────────

def _render_mapping_confidence():
    ui.space().classes("h-4")
    section_header("Mapping Confidence")
    summary = canonical_svc().get_summary()

    with ui.row().classes("w-full gap-4"):
        with ui.card().classes("p-4 text-center"):
            ui.circular_progress(value=summary["confidence"], min=0, max=1, size="xl",
                                 color=_conf_color(summary["confidence"]))
            ui.label(f"{summary['confidence'] * 100:.0f}%").classes("text-lg font-bold mt-1")
            ui.label("Overall").classes("text-xs text-gray-500")

        with ui.card().classes("flex-1 p-4"):
            _metric_row("Mapped", f"{summary['mapped']}/{summary['total']}", "positive")
            _metric_row("Ignored", str(summary["ignored"]), "info")
            _metric_row("Unmapped", str(summary["unmapped"]), "warning" if summary["unmapped"] > 0 else "grey")
            _metric_row("Required Missing", str(summary["required_missing"]),
                        "negative" if summary["required_missing"] > 0 else "positive")

        with ui.card().classes("flex-1 p-4"):
            ui.label("Confidence Breakdown").classes("text-sm font-semibold mb-2")
            svc_local = canonical_svc()
            for field in ["store", "upc", "description", "quantity", "price", "date"]:
                mapping = svc_local.get_mapping(field)
                conf = mapping.confidence if mapping else 0.0
                _confidence_row(field.title(), conf)


# ──────────────────────────────────────────────────────────────────
# Section 9 — Transformation Summary
# ──────────────────────────────────────────────────────────────────

def _render_transformation_summary():
    ui.space().classes("h-4")
    section_header("Transformation Summary")
    svc = canonical_svc()
    meta = svc.get_metadata()
    summary = svc.get_summary()

    with ui.grid(columns=2).classes("w-full gap-4"):
        with ui.card().classes("w-full p-4"):
            ui.label("Mapping Status").classes("text-sm font-bold mb-2")
            status_badge(f"{summary['mapped']} mapped", "success")
            status_badge(f"{summary['unmapped']} unmapped", "warning" if summary["unmapped"] > 0 else "info")
            status_badge(f"{summary['ignored']} ignored", "info")
            ui.label(f"Quantity: {summary['quantity']}").classes("text-sm mt-2")
            ui.label(f"UOM: {summary['uom']}").classes("text-sm")

        with ui.card().classes("w-full p-4"):
            ui.label("Transformation Log").classes("text-sm font-bold mb-2")
            for entry in meta.transformation_log:
                with ui.row().classes("items-center gap-2 py-1"):
                    ui.icon("arrow_right", color="grey").classes("text-sm")
                    ui.label(entry).classes("text-xs")


# ──────────────────────────────────────────────────────────────────
# Section 11 — Actions
# ──────────────────────────────────────────────────────────────────

def _render_actions():
    ui.space().classes("h-4")
    missing = canonical_svc().get_required_missing()

    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")

        with ui.row().classes("items-center gap-2"):
            ui.button("Auto Map", icon="auto_fix_high", color="primary",
                      on_click=lambda: canonical_ctrl().auto_map()).tooltip("Automatically detect column mappings")
            ui.button("Clear All", icon="clear",
                      on_click=lambda: canonical_ctrl().clear_all()).props("flat").tooltip("Clear all mappings")
            ui.button("Save Mapping", icon="save", color="positive",
                      on_click=lambda: canonical_ctrl().accept()).props("outline").tooltip("Save and accept mapping")
            ui.button("Continue", icon="arrow_forward", color="primary",
                      on_click=lambda: navigate_to("preview")).props("flat").tooltip("Proceed to Business Preview")

    if missing:
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.icon("warning", color="warning").classes("text-sm")
            ui.label(f"Required fields missing: {', '.join(missing)}").classes("text-sm text-warning")


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _summary_item(label: str, value: str) -> None:
    with ui.column().classes("gap-0"):
        ui.label(label).classes("text-xs text-gray-400")
        ui.label(value).classes("text-sm font-semibold")


def _progress_bar(value: float) -> ui.linear_progress:
    return ui.linear_progress(value=value, size="6px", color=_conf_color(value)).classes("min-w-16")


def _conf_color(v: float) -> str:
    return "positive" if v >= 0.9 else ("warning" if v >= 0.7 else "negative")


def navigate_canonical():
    """Navigate to Canonical Mapping workspace."""
    navigate_to("canonical")


def _metric_row(label: str, value: str, color: str) -> None:
    with ui.row().classes("items-center justify-between w-full py-1"):
        ui.label(label).classes("text-sm")
        ui.label(value).classes(f"text-sm font-semibold text-{color}")


def _confidence_row(label: str, value: float) -> None:
    with ui.row().classes("items-center gap-2 w-full py-1"):
        ui.label(label).classes("text-xs min-w-20")
        _progress_bar(value)
        ui.label(f"{value * 100:.0f}%").classes("text-xs font-mono text-gray-400")


# ──────────────────────────────────────────────────────────────────
# Render entry point
# ──────────────────────────────────────────────────────────────────

def render():
    render_guidance("canonical")
    _render_detection_summary()
    ui.space().classes("h-4")
    _render_physical_schema()
    ui.space().classes("h-4")
    _render_business_schema()
    _render_quantity_uom()
    _render_mapping_confidence()
    _render_transformation_summary()
    _render_actions()
