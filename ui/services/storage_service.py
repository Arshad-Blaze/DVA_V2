"""Storage service — low-level file I/O with Repository Pattern.

Provides atomic JSON file operations. No workspace or controller
should ever touch the filesystem directly — all persistence flows
through this service.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class StorageError(Exception):
    """Raised on storage-level failures."""


class StorageService:
    """Repository-pattern file storage with atomic writes.

    Currently backed by JSON files. Designed so SQLite can be
    substituted later without changing callers.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.join(Path.home(), ".dva")
        self._base = Path(base_dir)
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        dirs = [
            self._base / "projects",
            self._base / "connections",
            self._base / "sessions",
            self._base / "settings",
            self._base / "cache",
            self._base / "backups",
            self._base / "metadata",
            self._base / "logs",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @property
    def base_path(self) -> str:
        return str(self._base)

    # ------------------------------------------------------------------
    # Atomic JSON write
    # ------------------------------------------------------------------

    def write_json(self, subdir: str, filename: str, data: Any) -> None:
        """Atomically write a JSON file under base/subdir/filename.json."""
        filepath = self._base / subdir / f"{filename}.json"
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".tmp",
            dir=self._base / subdir,
            delete=False,
        )
        try:
            json.dump(data, tmp, indent=2, default=str)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp.close()
            os.replace(tmp.name, filepath)
        except Exception as e:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
            raise StorageError(f"Failed to write {filepath}: {e}") from e

    # ------------------------------------------------------------------
    # Atomic JSON append (list of records)
    # ------------------------------------------------------------------

    def append_json(self, subdir: str, filename: str, record: Any) -> None:
        """Append a record to a JSON array file (create if missing)."""
        data = self.read_json(subdir, filename, default=[])
        if not isinstance(data, list):
            data = []
        data.append(record)
        self.write_json(subdir, filename, data)

    # ------------------------------------------------------------------
    # JSON read
    # ------------------------------------------------------------------

    def read_json(self, subdir: str, filename: str,
                  default: Any = None) -> Any:
        """Read a JSON file; return default if missing or corrupt."""
        filepath = self._base / subdir / f"{filename}.json"
        if not filepath.exists():
            return default
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, subdir: str, filename: str) -> bool:
        """Delete a JSON file. Returns True if it existed."""
        filepath = self._base / subdir / f"{filename}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def delete_all(self, subdir: str) -> int:
        """Delete all JSON files in a subdirectory. Returns count."""
        count = 0
        dirpath = self._base / subdir
        if dirpath.exists():
            for f in dirpath.glob("*.json"):
                f.unlink()
                count += 1
        return count

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_files(self, subdir: str, suffix: str = ".json") -> List[str]:
        """List all files in subdir (stem names, no extension)."""
        dirpath = self._base / subdir
        if not dirpath.exists():
            return []
        return sorted(
            f.stem for f in dirpath.glob(f"*{suffix}")
        )

    # ------------------------------------------------------------------
    # Exists
    # ------------------------------------------------------------------

    def exists(self, subdir: str, filename: str) -> bool:
        return (self._base / subdir / f"{filename}.json").exists()

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------

    def create_backup(self, label: str = "") -> str:
        """Create a timestamped backup of the entire storage directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{label}" if label else ""
        backup_name = f"backup_{timestamp}{suffix}"
        backup_dir = self._base / "backups" / backup_name
        shutil.copytree(self._base, backup_dir,
                        ignore=shutil.ignore_patterns("backups"))
        return str(backup_dir)

    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups with metadata."""
        backup_dir = self._base / "backups"
        if not backup_dir.exists():
            return []
        backups = []
        for d in sorted(backup_dir.iterdir()):
            if d.is_dir():
                backups.append({
                    "name": d.name,
                    "path": str(d),
                    "created": datetime.fromtimestamp(d.stat().st_mtime),
                })
        return sorted(backups, key=lambda b: b["created"], reverse=True)

    def restore_backup(self, backup_name: str) -> bool:
        """Restore storage from a named backup. Returns success."""
        backup_dir = self._base / "backups" / backup_name
        if not backup_dir.exists():
            return False
        try:
            for item in self._base.iterdir():
                if item.name != "backups":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            for item in backup_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, self._base / item.name,
                                    dirs_exist_ok=True)
                else:
                    shutil.copy2(item, self._base / item.name)
            return True
        except (OSError, shutil.Error):
            return False

    # ------------------------------------------------------------------
    # Clear all data
    # ------------------------------------------------------------------

    def clear_all(self) -> None:
        """Wipe all storage (except backups)."""
        for subdir in ["projects", "connections", "sessions",
                       "settings", "cache", "metadata", "logs"]:
            self.delete_all(subdir)
