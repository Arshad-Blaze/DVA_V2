"""Detection-specific widgets — confidence, results, warnings, timeline, preview."""

from typing import Any, Dict, List, Optional

from nicegui import ui


def confidence_gauge(label: str, value: float, size: str = "md") -> ui.element:
    """Display a confidence value as a colored progress bar with label."""
    color = _confidence_color(value)
    pct = f"{value * 100:.0f}%"
    with ui.row().classes("items-center gap-3 w-full py-1") as row:
        ui.label(label).classes("text-sm min-w-32")
        ui.linear_progress(value=value, size="20px", color=color).classes("flex-1")
        ui.label(pct).classes(f"text-xs font-mono min-w-10 text-{color}")
    return row


def confidence_circle(label: str, value: float) -> ui.element:
    """Display a circular confidence indicator."""
    color = _confidence_color(value)
    pct = f"{value * 100:.0f}%"
    with ui.row().classes("flex-col items-center gap-1 p-3") as row:
        ui.circular_progress(value=value, min=0, max=1, size="xl", color=color)
        ui.label(pct).classes(f"text-lg font-bold text-{color}")
        ui.label(label).classes("text-xs text-gray-500 text-center")
    return row


def detection_result_card(label: str, value: str, confidence: float,
                           explanation: str = "", override: Optional[str] = None) -> ui.card:
    """Display a single detection result with confidence and optional override."""
    color = _confidence_color(confidence)
    with ui.card().classes("w-full p-4") as card:
        with ui.row().classes("items-center justify-between w-full"):
            ui.label(label).classes("text-sm font-semibold text-gray-600")
            _confidence_badge(confidence)

        ui.label(value).classes("text-xl font-bold mt-1")

        if explanation:
            ui.label(explanation).classes("text-xs text-gray-400 mt-1")

        if override is not None:
            with ui.row().classes("items-center gap-2 mt-2 p-2 bg-warning-50 rounded"):
                ui.icon("edit", color="warning").classes("text-sm")
                ui.label(f"Override: {override}").classes("text-xs text-warning font-semibold")

        with ui.row().classes("items-center gap-1 mt-2"):
            ui.linear_progress(value=confidence, size="6px", color=color).classes("flex-1")
            ui.label(f"{confidence * 100:.0f}%").classes("text-xs font-mono text-gray-400")
    return card


def warning_banner(warning: Dict[str, Any]) -> ui.card:
    """Display a warning/suggestion/info banner."""
    wtype = warning.get("type", "info")
    msg = warning.get("message", "")
    detail = warning.get("detail", "")
    icon_map = {"warning": "warning", "info": "info", "suggestion": "lightbulb"}
    color_map = {"warning": "warning", "info": "info", "suggestion": "positive"}
    icon = icon_map.get(wtype, "info")
    color = color_map.get(wtype, "info")

    with ui.card().classes(f"w-full p-3 border-l-4 border-{color} cursor-pointer") as card:
        with ui.row().classes("items-center gap-2"):
            ui.icon(icon, color=color).classes("text-lg")
            with ui.column().classes("gap-0"):
                ui.label(msg).classes("text-sm font-medium")
                if detail:
                    ui.label(detail).classes("text-xs text-gray-500 mt-1")
    return card


def explanation_panel(title: str, value: str, reason: str,
                       confidence: float) -> ui.card:
    """Display a detected value with its explanation."""
    color = _confidence_color(confidence)
    with ui.card().classes("w-full p-4") as card:
        with ui.row().classes("items-center justify-between"):
            ui.label(title).classes("text-sm font-semibold")
            _confidence_badge(confidence)
        ui.label(value).classes("text-2xl font-bold mt-1")
        ui.label(reason).classes("text-xs text-gray-500 mt-2 italic")
        ui.linear_progress(value=confidence, size="4px", color=color).classes("w-full mt-2")
    return card


def timeline_view(steps: List[Dict[str, Any]]) -> ui.column:
    """Display a vertical timeline of detection steps."""
    with ui.column().classes("w-full gap-2") as col:
        for i, step in enumerate(steps):
            status = step.get("status", "pending")
            label = step.get("step", "")
            detail = step.get("detail", "")
            is_last = i == len(steps) - 1

            icon_map = {"completed": "check_circle", "running": "circle", "pending": "radio_button_unchecked"}
            color_map = {"completed": "positive", "running": "primary", "pending": "grey"}

            with ui.row().classes("items-start gap-3"):
                with ui.column().classes("items-center"):
                    ui.icon(icon_map.get(status, "circle"),
                            color=color_map.get(status, "grey")).classes("text-lg")
                    if not is_last:
                        ui.html('<div style="width:2px;height:24px;background:#e0e0e0;"></div>')
                with ui.column().classes("gap-0"):
                    ui.label(label).classes(f"text-sm {'font-semibold' if status == 'completed' else ''}")
                    if detail:
                        ui.label(detail).classes("text-xs text-gray-400")
    return col


def raw_preview_viewer(lines: List[str], max_lines: int = 20) -> ui.element:
    """Display a raw file preview with line numbers (monospace)."""
    shown = lines[:max_lines]
    html_lines = []
    for i, line in enumerate(shown):
        escaped = (line or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_lines.append(
            f'<div style="display:flex;">'
            f'<span style="color:#999;min-width:40px;text-align:right;padding-right:12px;'
            f'user-select:none;font-family:var(--font-mono);font-size:12px;">{i + 1}</span>'
            f'<span style="font-family:var(--font-mono);font-size:13px;white-space:pre-wrap;">{escaped}</span>'
            f'</div>'
        )
    return ui.html(
        f'<div style="background:#1a1a2e;color:#e0e0e0;padding:16px;border-radius:8px;'
        f'overflow-x:auto;max-height:500px;overflow-y:auto;">'
        f'{"".join(html_lines)}'
        f'</div>'
    )


def connection_summary_card(label: str, value: str, icon: str = "link") -> ui.element:
    """Display a connection summary item."""
    with ui.row().classes("items-center gap-2") as row:
        ui.icon(icon, color="grey").classes("text-sm")
        ui.label(label).classes("text-xs text-gray-400")
        ui.label(value).classes("text-sm font-semibold")
    return row


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _confidence_color(value: float) -> str:
    if value >= 0.9:
        return "positive"
    elif value >= 0.7:
        return "warning"
    return "negative"


def _confidence_badge(value: float) -> ui.html:
    color = _confidence_color(value)
    label = "High" if value >= 0.9 else ("Medium" if value >= 0.7 else "Low")
    return ui.html(
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'padding:2px 8px;border-radius:12px;font-size:11px;font-weight:500;'
        f'background:var(--{color});color:#fff;">{label}</span>'
    )
