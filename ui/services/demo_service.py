"""Demo service — manages demo mode for first-run experience.

When demo mode is active, demo data is loaded from the /demo directory.
When demo mode exits, all temporary demo data is cleaned up.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

DEMO_DIR = Path(__file__).parent.parent.parent / "demo"

RETAILER_SAMPLES = [
    {"id": "retailer_sample_1", "name": "Retailer Sample 1", "path": "retailer_sample_1/sales_data.csv"},
    {"id": "retailer_sample_2", "name": "Retailer Sample 2", "path": "retailer_sample_2/inventory.csv"},
    {"id": "retailer_sample_3", "name": "Retailer Sample 3", "path": "retailer_sample_3/transactions.csv"},
]


class DemoService:
    def __init__(self, project_service=None, connection_service=None, detection_service=None,
                 canonical_service=None, preview_service=None):
        self._active: bool = False
        self._demo_project_id: Optional[str] = None
        self._temp_dir: Optional[Path] = None
        self._on_change: Optional[Callable] = None

        self._project_svc = project_service
        self._conn_svc = connection_service
        self._detection_svc = detection_service
        self._canonical_svc = canonical_service
        self._preview_svc = preview_service

    @property
    def is_active(self) -> bool:
        return self._active

    def start_demo(self) -> bool:
        if self._active:
            return False
        try:
            self._temp_dir = Path(os.path.join(str(Path.home()), ".dva", "demo_temp"))
            self._temp_dir.mkdir(parents=True, exist_ok=True)

            if self._project_svc:
                project = self._project_svc.create_project(
                    name="Demo Project",
                    description="Temporary demo project for exploring DVA",
                    source=str(self._temp_dir)
                )
                self._demo_project_id = project["id"]

            if self._conn_svc:
                self._conn_svc.add_connection(
                    name="Demo Connection",
                    conn_type="local",
                    path=str(self._temp_dir),
                    description="Demo data connection"
                )

            self._active = True
            self._notify()
            return True
        except Exception:
            self._cleanup()
            return False

    def stop_demo(self) -> bool:
        if not self._active:
            return False
        self._cleanup()
        self._active = False
        self._notify()
        return True

    def _cleanup(self) -> None:
        if self._project_svc and self._demo_project_id:
            self._project_svc.delete_project(self._demo_project_id)
            self._demo_project_id = None
        if self._conn_svc:
            conns = self._conn_svc.list_connections()
            for c in conns:
                if "demo" in c.get("name", "").lower():
                    self._conn_svc.remove_connection(c["id"])
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(str(self._temp_dir))
            self._temp_dir = None

    def get_sample_list(self) -> List[Dict[str, Any]]:
        return [dict(s) for s in RETAILER_SAMPLES]

    def get_sample_path(self, sample_id: str) -> Optional[str]:
        for s in RETAILER_SAMPLES:
            if s["id"] == sample_id:
                return str(DEMO_DIR / s["path"])
        return None

    def reset(self) -> None:
        self._active = False
        self._demo_project_id = None
        self._temp_dir = None

    def on_change(self, callback: Callable) -> None:
        self._on_change = callback

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()
