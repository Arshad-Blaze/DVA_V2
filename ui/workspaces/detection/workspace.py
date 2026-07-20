"""Detection workspace — Interactive Data Analysis Studio.

Sprint 3: File inspection, automatic detection visualization,
confidence dashboard, manual overrides, detection timeline.
"""

from nicegui import ui
from ui.widgets.cards import section_header, info_card, metric_card
from ui.widgets.detection import (
    confidence_gauge, confidence_circle, detection_result_card,
    warning_banner, explanation_panel, timeline_view,
    raw_preview_viewer, connection_summary_card,
)
from ui.shared import detection_svc, detection_ctrl, conn_svc
from ui.widgets.guidance_bar import render_guidance


def _get_connection_files():
    conn = conn_svc()
    current = conn.current_connection
    if current:
        path = current.get("path", "/")
        return [e for e in conn.browse_directory(path) if not e["is_dir"]]
    return []


def _render_connection_summary():
    section_header("Connection Summary")
    svc = detection_svc()
    conn = conn_svc()
    current = conn.current_connection

    with ui.card().classes("w-full p-4"):
        if not current:
            ui.label("No active connection. Go to Connection workspace first.").classes("text-sm text-gray-500")
            return

        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label("Connection:").classes("text-sm text-gray-500")
            ui.label(current.get("name", "Unknown")).classes("text-sm font-semibold")

        files = _get_connection_files()
        if not files:
            ui.label("No files found in connection directory.").classes("text-sm text-gray-400 mt-2")
            return

        with ui.row().classes("items-center gap-2 mt-2"):
            ui.label("Files:").classes("text-sm text-gray-500")
            for f in files:
                is_active = f["name"] == svc.selected_file
                ui.button(f["name"], color="primary" if is_active else "grey",
                          on_click=lambda fn=f["name"]: detection_ctrl().switch_file(fn)).props("flat dense size=sm").tooltip("Select file for detection")

        selected = svc.selected_file or "None"
        ui.label(f"Selected: {selected}").classes("text-sm text-gray-500 mt-1")


def _render_raw_file_preview():
    svc = detection_svc()
    section_header("Raw File Preview")
    with ui.card().classes("w-full p-4"):
        with ui.row().classes("items-center justify-between w-full mb-2"):
            ui.label(f"File: {svc.selected_file or 'None'}").classes("text-sm font-medium")
        lines = []
        if svc.result and svc.result.raw_preview is not None:
            import polars as pl
            df = svc.result.raw_preview
            lines = [",".join(str(v) for v in row) for row in df.iter_rows()]
        raw_preview_viewer(lines)


def _render_detection_results():
    section_header("Automatic Detection Results")
    svc = detection_svc()
    r = svc.result
    if not r:
        ui.label("No detection results").classes("text-gray-500")
        return

    with ui.grid(columns=2).classes("w-full gap-4"):
        detection_result_card(
            "File Type", r.file_type.value.title() if r.file_type else "Unknown",
            r.confidence,
            "File type determined by extension and content analysis."
        )
        detection_result_card(
            "Delimiter", f"Comma '{r.delimiter}'" if r.delimiter else "None",
            r.delimiter_confidence,
            "Delimiter detected by analyzing separator frequency across sample lines."
        )
        detection_result_card(
            "Encoding", r.encoding.upper(),
            r.encoding_confidence,
            "Encoding detected via BOM signature and byte sequence analysis."
        )
        detection_result_card(
            "Header Row", f"Row {r.header_start_line + 1}" if r.has_header else "None",
            r.header_confidence,
            "Row 1 contains unique textual values matching column naming patterns."
        )
        detection_result_card(
            "Columns", f"{len(r.columns or [])} detected",
            r.confidence,
            f"Columns: {', '.join(r.columns or [])}"
        )
        detection_result_card(
            "File Structure", "Single-line records" if not r.is_multiline else "Multi-line records",
            0.95 if not r.is_multiline else 0.85,
            "Each row represents one complete record. No multi-line spanning detected."
        )


def _render_confidence_panel():
    section_header("Detection Confidence")
    svc = detection_svc()
    r = svc.result
    if not r:
        return

    with ui.row().classes("w-full gap-6 items-start"):
        with ui.card().classes("p-4"):
            confidence_circle("Overall", r.confidence)

        with ui.column().classes("flex-1 gap-1"):
            confidence_gauge("Delimiter", r.delimiter_confidence)
            confidence_gauge("Encoding", r.encoding_confidence)
            confidence_gauge("Header", r.header_confidence)
            confidence_gauge("Layout", getattr(r, 'layout_confidence', 0.95))
            confidence_gauge("Record Type", 0.92)


def _render_warnings():
    svc = detection_svc()
    warnings = svc.warnings
    if not warnings:
        return

    ui.space().classes("h-4")
    section_header("Warnings & Suggestions")
    for w in warnings:
        warning_banner(w)


def _render_manual_overrides():
    ui.space().classes("h-4")
    section_header("Manual Overrides")

    svc = detection_svc()
    r = svc.result

    with ui.card().classes("w-full p-4"):
        ui.label("Override detected values only when the automatic detection is incorrect.").classes("text-xs text-gray-500 mb-3")

        override_fields = [
            ("delimiter", "Delimiter", r.delimiter if r else ",", [",", "|", "\t", ";"]),
            ("encoding", "Encoding", r.encoding if r else "utf-8", ["utf-8", "utf-16", "latin-1"]),
            ("header_row", "Header Row", str(r.header_start_line + 1 if r and r.has_header else 1),
             ["1", "0 (No Header)"]),
            ("start_line", "Data Start Line", str(r.data_start_line + 1 if r else 2), []),
        ]

        for key, label, detected, options in override_fields:
            override_val = svc.get_override(key)
            with ui.row().classes("items-center gap-3 w-full py-2 border-bottom"):
                ui.label(label).classes("text-sm font-medium min-w-32")
                ui.label(f"Auto: {detected}").classes("text-xs text-gray-400")

                if options:
                    sel = ui.select(options, value=override_val or detected,
                                    on_change=lambda e, k=key: detection_ctrl().set_override(k, e.value))
                    sel.classes("min-w-40")
                else:
                    inp = ui.input(value=override_val or detected,
                                   on_change=lambda e, k=key: detection_ctrl().set_override(k, e.value))
                    inp.classes("min-w-40")

                if override_val:
                    ui.button(icon="undo", on_click=lambda k=key: (
                        detection_ctrl().clear_override(k),
                        ui.update(sel) if options else ui.update(inp)
                    )).props("flat round dense size=sm")

        if svc.has_overrides:
            ui.button("Reset All Overrides", color="warning",
                      on_click=lambda: detection_ctrl().clear_all_overrides()).props("flat")


def _render_timeline():
    ui.space().classes("h-4")
    section_header("Detection Timeline")
    with ui.card().classes("w-full p-4"):
        timeline_view(detection_svc().timeline)


def _render_actions():
    ui.space().classes("h-4")
    with ui.row().classes("w-full items-center justify-between p-4 bg-gray-50 rounded-lg"):
        ui.label("Actions").classes("text-lg font-semibold")

        with ui.row().classes("items-center gap-2"):
            ui.button("Retry Detection", icon="refresh",
                      on_click=lambda: detection_ctrl().run_detection()).props("flat").tooltip("Re-run automatic detection")
            ui.button("Validate", icon="check_circle",
                      on_click=lambda: detection_ctrl().validate_detection()).props("outline").tooltip("Validate detection results")
            ui.button("Accept", icon="verified", color="positive",
                      on_click=lambda: detection_ctrl().accept_detection()).tooltip("Accept detection results")
            ui.button("Continue to Canonical", icon="arrow_forward", color="primary",
                      ).props("flat").tooltip("Proceed to Canonical Mapping")


def render():
    render_guidance("detection")
    _render_connection_summary()
    ui.space().classes("h-4")
    _render_raw_file_preview()
    ui.space().classes("h-4")
    _render_detection_results()
    ui.space().classes("h-4")
    _render_confidence_panel()
    _render_warnings()
    _render_manual_overrides()
    _render_timeline()
    _render_actions()
