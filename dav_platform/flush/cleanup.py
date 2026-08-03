"""Flush Layer — File and Resource Cleanup Manager."""

import os
import shutil
from typing import Any, Dict, List, Optional


class CleanupManager:
    """Orchestrates cleanup of temporary files, directories, and exports."""

    def __init__(self):
        self._temp_dirs: List[str] = []
        self._temp_files: List[str] = []

    def register_temp_dir(self, path: str) -> None:
        self._temp_dirs.append(path)

    def register_temp_file(self, path: str) -> None:
        self._temp_files.append(path)

    def delete_temp_files(self, retain: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "temp_file_cleanup", "dry_run": True, "status": "skipped",
                    "files_found": len(self._temp_files)}
        retain = retain or []
        deleted = 0
        errors = []
        for f in self._temp_files:
            if f in retain:
                continue
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    deleted += 1
            except Exception as e:
                errors.append(str(e))
        self._temp_files = [f for f in self._temp_files if f in retain]
        result = {"action": "temp_file_cleanup", "files_deleted": deleted, "status": "completed"}
        if errors:
            result["errors"] = errors
        return result

    def delete_temp_dirs(self, retain: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "temp_dir_cleanup", "dry_run": True, "status": "skipped",
                    "dirs_found": len(self._temp_dirs)}
        retain = retain or []
        deleted = 0
        errors = []
        for d in self._temp_dirs:
            if d in retain:
                continue
            try:
                if os.path.isdir(d):
                    shutil.rmtree(d, ignore_errors=True)
                    deleted += 1
            except Exception as e:
                errors.append(str(e))
        self._temp_dirs = [d for d in self._temp_dirs if d in retain]
        result = {"action": "temp_dir_cleanup", "dirs_deleted": deleted, "status": "completed"}
        if errors:
            result["errors"] = errors
        return result

    def delete_exports(self, export_files: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            return {"action": "export_cleanup", "dry_run": True, "status": "skipped",
                    "files_found": len(export_files or [])}
        export_files = export_files or []
        deleted = 0
        errors = []
        for f in export_files:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    deleted += 1
            except Exception as e:
                errors.append(str(e))
        result = {"action": "export_cleanup", "files_deleted": deleted, "status": "completed"}
        if errors:
            result["errors"] = errors
        return result

    @property
    def temp_file_count(self) -> int:
        return len(self._temp_files)

    @property
    def temp_dir_count(self) -> int:
        return len(self._temp_dirs)
