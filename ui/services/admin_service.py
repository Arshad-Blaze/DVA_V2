"""Admin service — Administration, History & Diagnostics Center (Sprint 9).

System health, project/execution history, log viewer, diagnostics,
storage, settings, maintenance, and about.

Never performs admin actions — only visualizes and configures.
"""

import csv
import io
from typing import Any, Callable, Dict, List, Optional


SYSTEM_HEALTH_DEMO = {
    "cpu": {"usage_pct": 23, "cores": 8, "status": "healthy"},
    "memory": {"total_gb": 16, "used_gb": 5.2, "available_gb": 10.8, "usage_pct": 32.5, "status": "healthy"},
    "streaming": {"active": True, "uptime": "12h 34m", "status": "healthy"},
    "projects": {"total": 2, "active": 1, "status": "healthy"},
    "reports": {"total": 5, "generated_today": 2, "status": "healthy"},
    "storage": {"used_mb": 128, "available_mb": 2048, "total_mb": 2176, "status": "healthy"},
    "cache": {"entries": 342, "size_mb": 18, "status": "healthy"},
    "connections": {"total": 1, "active": 1, "status": "healthy"},
    "version": {"app": "v2.0.0", "backend": "v3.1.0", "ui": "v2.0.0"},
}

PROJECT_HISTORY_DEMO = [
    {"name": "Retail Sales Q1 2026", "created": "2026-07-15", "modified": "2026-07-19", "retailer": "RetailCo", "version": "v2.3", "status": "active"},
    {"name": "Retail Sales Q4 2025", "created": "2026-04-01", "modified": "2026-04-15", "retailer": "RetailCo", "version": "v1.5", "status": "archived"},
]

EXECUTION_HISTORY_DEMO = [
    {"execution_id": "EXEC-001", "project": "Retail Sales Q1 2026", "runtime": "4.2s", "status": "completed", "rows": 1250, "validation_score": 80.0, "reports": 5},
    {"execution_id": "EXEC-002", "project": "Retail Sales Q1 2026", "runtime": "3.8s", "status": "completed", "rows": 1250, "validation_score": 85.0, "reports": 3},
    {"execution_id": "EXEC-003", "project": "Retail Sales Q4 2025", "runtime": "5.1s", "status": "completed", "rows": 1100, "validation_score": 92.0, "reports": 4},
    {"execution_id": "EXEC-004", "project": "Retail Sales Q1 2026", "runtime": "2.9s", "status": "failed", "rows": 0, "validation_score": 0.0, "reports": 0},
]

LOGS_DEMO = [
    {"timestamp": "2026-07-19 14:32:05", "severity": "info", "source": "execution", "message": "Execution EXEC-001 completed successfully"},
    {"timestamp": "2026-07-19 14:32:04", "severity": "warning", "source": "validation", "message": "Store S045 has zero total sales"},
    {"timestamp": "2026-07-19 14:32:03", "severity": "info", "source": "execution", "message": "Processing pipeline stage 5/6 complete"},
    {"timestamp": "2026-07-19 14:32:02", "severity": "info", "source": "execution", "message": "Processing pipeline stage 4/6 complete"},
    {"timestamp": "2026-07-19 14:32:01", "severity": "error", "source": "validation", "message": "UPC 490123456999 has negative price (-$2.99)"},
    {"timestamp": "2026-07-19 14:32:00", "severity": "info", "source": "execution", "message": "Processing pipeline stage 3/6 complete"},
    {"timestamp": "2026-07-19 14:31:59", "severity": "warning", "source": "mapping", "message": "Low confidence mapping for Promotion column (85%)"},
    {"timestamp": "2026-07-19 14:31:58", "severity": "info", "source": "execution", "message": "Processing pipeline stage 2/6 complete"},
    {"timestamp": "2026-07-19 14:31:57", "severity": "info", "source": "execution", "message": "Processing pipeline stage 1/6 complete"},
    {"timestamp": "2026-07-19 14:31:55", "severity": "info", "source": "execution", "message": "Execution EXEC-001 started"},
]

DIAGNOSTICS_DEMO = {
    "architecture": {"status": "passed", "layers": 9, "description": "All 9 layers verified"},
    "contracts": {"status": "passed", "contracts": 42, "description": "All contracts validated"},
    "regression": {"status": "passed", "tests": 1236, "description": "All regression tests passing"},
    "performance": {"status": "passed", "baseline_ms": 45, "description": "Under 50ms threshold"},
    "version": {"app": "v2.0.0", "backend": "v3.1.0", "ui": "v2.0.0"},
}

STORAGE_DEMO = {
    "projects": {"count": 2, "size_mb": 4.5},
    "reports": {"count": 5, "size_mb": 2.1},
    "cache": {"entries": 342, "size_mb": 18.0},
    "logs": {"count": 10, "size_mb": 0.05},
    "exports": {"count": 3, "size_mb": 1.2},
    "temp": {"count": 12, "size_mb": 8.3},
    "total_used_mb": 34.15,
    "total_available_mb": 2048,
}

SETTINGS_DEMO = {
    "application": {"name": "DVA Platform", "version": "v2.0.0", "language": "English", "timezone": "UTC"},
    "theme": {"dark_mode": False, "accent_color": "blue", "font_size": "medium"},
    "workspace": {"auto_save": True, "confirm_on_exit": True, "show_status_bar": True},
    "preferences": {"rows_per_page": 50, "max_recent_projects": 10, "auto_refresh_interval": 30},
    "reports": {"default_format": "csv", "include_charts": True, "max_history": 20},
    "notifications": {"show_success": True, "show_warnings": True, "show_errors": True, "sound_enabled": False},
    "shortcuts": {"save": "Ctrl+S", "navigate": "Ctrl+K", "search": "Ctrl+F", "export": "Ctrl+E"},
}

MAINTENANCE_ACTIONS_DEMO = [
    {"id": "clear_cache", "label": "Clear Cache", "description": "Remove cached data (18 MB)", "icon": "delete_sweep", "severity": "info"},
    {"id": "delete_temp", "label": "Delete Temp Files", "description": "Remove temporary files (8.3 MB)", "icon": "cleaning_services", "severity": "info"},
    {"id": "repair", "label": "Repair Workspace", "description": "Repair workspace configuration and state", "icon": "build", "severity": "warning"},
    {"id": "backup", "label": "Backup Configuration", "description": "Create a full configuration backup", "icon": "backup", "severity": "info"},
    {"id": "restore", "label": "Restore Configuration", "description": "Restore from a previous backup", "icon": "restore", "severity": "warning"},
    {"id": "export_config", "label": "Export Configuration", "description": "Export settings to JSON file", "icon": "file_download", "severity": "info"},
    {"id": "import_config", "label": "Import Configuration", "description": "Import settings from JSON file", "icon": "file_upload", "severity": "warning"},
]

ABOUT_DEMO = {
    "version": "v2.0.0",
    "architecture": "9-Layer Pipeline Architecture",
    "backend": "Python 3.12, 1236+ tests",
    "ui": "NiceGUI v3.14.0, 400+ tests",
    "git_tag": "v2.0-complete",
    "build": "2026-07-19",
    "license": "Proprietary",
    "credits": "DVA Platform Team",
}


class AdminService:
    """Manages Administration Center state.

    Never performs admin actions — only visualizes and configures.
    """

    def __init__(self, context=None):
        self._context = context
        self._log_search: str = ""
        self._log_severity: Optional[str] = None
        self._log_source: Optional[str] = None
        self._selected_execution: Optional[str] = None
        self._selected_project: Optional[str] = None
        self._selected_log: Optional[int] = None
        self._settings_overrides: Dict[str, Any] = {}
        self._on_change: Optional[Callable] = None

    # ── System Health ────────────────────────────────────────

    @property
    def system_health(self) -> Dict[str, Any]:
        return {k: dict(v) if isinstance(v, dict) else v for k, v in SYSTEM_HEALTH_DEMO.items()}

    # ── Project History ──────────────────────────────────────

    @property
    def project_history(self) -> List[Dict[str, Any]]:
        return [dict(p) for p in PROJECT_HISTORY_DEMO]

    def select_project(self, name: str) -> None:
        self._selected_project = name
        self._notify()

    @property
    def selected_project(self) -> Optional[Dict[str, Any]]:
        for p in PROJECT_HISTORY_DEMO:
            if p["name"] == self._selected_project:
                return dict(p)
        return None

    # ── Execution History ────────────────────────────────────

    @property
    def execution_history(self) -> List[Dict[str, Any]]:
        return [dict(e) for e in EXECUTION_HISTORY_DEMO]

    def select_execution(self, exec_id: str) -> None:
        self._selected_execution = exec_id
        self._notify()

    @property
    def selected_execution(self) -> Optional[Dict[str, Any]]:
        for e in EXECUTION_HISTORY_DEMO:
            if e["execution_id"] == self._selected_execution:
                return dict(e)
        return None

    # ── Log Viewer ───────────────────────────────────────────

    @property
    def all_logs(self) -> List[Dict[str, Any]]:
        return [dict(l) for l in LOGS_DEMO]

    @property
    def filtered_logs(self) -> List[Dict[str, Any]]:
        logs = self.all_logs
        if self._log_severity and self._log_severity != "all":
            logs = [l for l in logs if l["severity"] == self._log_severity]
        if self._log_source and self._log_source != "all":
            logs = [l for l in logs if l["source"] == self._log_source]
        if self._log_search:
            q = self._log_search.lower()
            logs = [l for l in logs if q in l["message"].lower()]
        return logs

    @property
    def log_sources(self) -> List[str]:
        sources = set(l["source"] for l in LOGS_DEMO)
        return sorted(sources)

    def set_log_search(self, query: str) -> None:
        self._log_search = query
        self._notify()

    def set_log_severity(self, severity: Optional[str]) -> None:
        self._log_severity = severity if severity != "all" else None
        self._notify()

    def set_log_source(self, source: Optional[str]) -> None:
        self._log_source = source if source != "all" else None
        self._notify()

    def select_log(self, index: int) -> None:
        self._selected_log = index
        self._notify()

    @property
    def selected_log(self) -> Optional[Dict[str, Any]]:
        logs = self.filtered_logs
        if self._selected_log is not None and self._selected_log < len(logs):
            return dict(logs[self._selected_log])
        return None

    def export_logs(self) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["Timestamp", "Severity", "Source", "Message"])
        for log in self.filtered_logs:
            w.writerow([log["timestamp"], log["severity"], log["source"], log["message"]])
        return buf.getvalue()

    # ── Diagnostics ──────────────────────────────────────────

    @property
    def diagnostics(self) -> Dict[str, Any]:
        return {k: dict(v) if isinstance(v, dict) else v for k, v in DIAGNOSTICS_DEMO.items()}

    # ── Storage ──────────────────────────────────────────────

    @property
    def storage(self) -> Dict[str, Any]:
        return dict(STORAGE_DEMO)

    # ── Settings ─────────────────────────────────────────────

    @property
    def default_settings(self) -> Dict[str, Any]:
        return {k: dict(v) if isinstance(v, dict) else v for k, v in SETTINGS_DEMO.items()}

    @property
    def settings(self) -> Dict[str, Any]:
        merged = {}
        for section, values in SETTINGS_DEMO.items():
            overrides = self._settings_overrides.get(section, {})
            merged[section] = {**values, **overrides}
        return merged

    def update_setting(self, section: str, key: str, value: Any) -> None:
        if section not in self._settings_overrides:
            self._settings_overrides[section] = {}
        self._settings_overrides[section][key] = value
        self._notify()

    def reset_settings(self) -> None:
        self._settings_overrides = {}
        self._notify()

    # ── Maintenance ──────────────────────────────────────────

    @property
    def maintenance_actions(self) -> List[Dict[str, Any]]:
        return [dict(a) for a in MAINTENANCE_ACTIONS_DEMO]

    def run_maintenance(self, action_id: str) -> str:
        for a in MAINTENANCE_ACTIONS_DEMO:
            if a["id"] == action_id:
                return f"Maintenance action '{a['label']}' completed successfully"
        return f"Unknown action: {action_id}"

    # ── About ────────────────────────────────────────────────

    @property
    def about(self) -> Dict[str, Any]:
        return dict(ABOUT_DEMO)

    # ── Status Bar ───────────────────────────────────────────

    @property
    def status_bar(self) -> Dict[str, Any]:
        health = SYSTEM_HEALTH_DEMO
        return {
            "health": health["cpu"]["status"],
            "memory": f"{health['memory']['usage_pct']:.0f}%",
            "version": health["version"]["app"],
        }

    # ── Events ───────────────────────────────────────────────

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
