"""Migration service — storage versioning & automatic migration.

Ensures persisted data can evolve without breaking existing
installations. Schema migrations run automatically on startup.
"""

from typing import Any, Callable, Dict, List

from ui.services.storage_service import StorageService


CURRENT_STORAGE_VERSION = 1


class MigrationService:
    """Manages storage schema versioning and migrations."""

    def __init__(self, storage: StorageService):
        self._storage = storage
        self._migrations: Dict[int, Callable] = {
            # Future migrations register here:
            # 2: _migrate_v1_to_v2,
        }
        self._migration_log: List[str] = []

    def current_version(self) -> int:
        return CURRENT_STORAGE_VERSION

    def _read_metadata(self) -> Dict[str, Any]:
        meta = self._storage.read_json("metadata", "version", default={})
        if not isinstance(meta, dict):
            return {}
        return meta

    def _write_metadata(self, meta: Dict[str, Any]) -> None:
        self._storage.write_json("metadata", "version", meta)

    def stored_version(self) -> int:
        meta = self._read_metadata()
        return meta.get("storage_version", 0)

    def run(self) -> List[str]:
        """Run pending migrations in order. Returns migration log."""
        stored = self.stored_version()
        current = CURRENT_STORAGE_VERSION

        if stored > current:
            raise RuntimeError(
                f"Storage version {stored} is newer than application "
                f"version {current}. Downgrade not supported."
            )

        if stored == current:
            return []

        for version in range(stored + 1, current + 1):
            migrator = self._migrations.get(version)
            if migrator:
                migrator()
                self._migration_log.append(
                    f"Migrated storage v{version - 1} → v{version}"
                )

        self._write_metadata({
            "storage_version": CURRENT_STORAGE_VERSION,
            "application_version": "2.0.2",
            "migrated_at": None,  # filled by serialization's default=str
        })
        self._migration_log.append(
            f"Storage at version {CURRENT_STORAGE_VERSION}"
        )
        return self._migration_log

    def migration_log(self) -> List[str]:
        return list(self._migration_log)
