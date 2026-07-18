"""UI Tests — Persistence Layer (Sprint 2.5).

StorageService, SerializationService, MigrationService,
PersistenceService, WorkspaceContext, Backup/Restore.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ui.services.storage_service import StorageService, StorageError
from ui.services.serialization_service import (
    serialize_project, deserialize_project,
    serialize_connection, deserialize_connection,
    serialize_context, deserialize_context,
    serialize_projects, deserialize_projects,
)
from ui.services.migration_service import MigrationService, CURRENT_STORAGE_VERSION
from ui.services.persistence_service import PersistenceService
from ui.services.workspace_context import WorkspaceContext


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def temp_storage():
    """Create a StorageService backed by a temp directory."""
    tmpdir = tempfile.mkdtemp(prefix="dva_test_")
    svc = StorageService(base_dir=tmpdir)
    yield svc
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def temp_persistence(temp_storage):
    """Create a full PersistenceService stack in a temp dir."""
    ctx = WorkspaceContext()
    mig = MigrationService(temp_storage)
    ps = PersistenceService(temp_storage, mig, ctx)
    ps.run_migrations()
    return ps, ctx, temp_storage


# ======================================================================
# StorageService
# ======================================================================

class TestStorageService:
    def test_write_and_read(self, temp_storage):
        temp_storage.write_json("projects", "test", {"key": "value"})
        data = temp_storage.read_json("projects", "test")
        assert data == {"key": "value"}

    def test_read_missing_default(self, temp_storage):
        data = temp_storage.read_json("projects", "nonexistent", default=[1, 2, 3])
        assert data == [1, 2, 3]

    def test_read_missing_none(self, temp_storage):
        data = temp_storage.read_json("projects", "nonexistent")
        assert data is None

    def test_delete(self, temp_storage):
        temp_storage.write_json("projects", "del_test", {"x": 1})
        assert temp_storage.exists("projects", "del_test") is True
        result = temp_storage.delete("projects", "del_test")
        assert result is True
        assert temp_storage.exists("projects", "del_test") is False

    def test_delete_nonexistent(self, temp_storage):
        result = temp_storage.delete("projects", "nope")
        assert result is False

    def test_delete_all(self, temp_storage):
        temp_storage.write_json("projects", "a", {})
        temp_storage.write_json("projects", "b", {})
        count = temp_storage.delete_all("projects")
        assert count == 2

    def test_list_files(self, temp_storage):
        temp_storage.write_json("projects", "alpha", {})
        temp_storage.write_json("projects", "beta", {})
        files = temp_storage.list_files("projects")
        assert files == ["alpha", "beta"]

    def test_list_files_empty(self, temp_storage):
        files = temp_storage.list_files("empty_dir")
        assert files == []

    def test_append_json(self, temp_storage):
        temp_storage.append_json("projects", "append_test", {"id": 1})
        temp_storage.append_json("projects", "append_test", {"id": 2})
        data = temp_storage.read_json("projects", "append_test")
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2

    def test_base_path(self, temp_storage):
        path = temp_storage.base_path
        assert os.path.isdir(path)

    def test_ensure_dirs_creates_structure(self, temp_storage):
        svc = temp_storage
        for subdir in ["projects", "connections", "sessions", "settings",
                        "cache", "backups", "metadata", "logs"]:
            assert os.path.isdir(os.path.join(svc.base_path, subdir))

    def test_clear_all(self, temp_storage):
        temp_storage.write_json("projects", "p1", {})
        temp_storage.write_json("connections", "c1", {})
        temp_storage.clear_all()
        assert temp_storage.list_files("projects") == []
        assert temp_storage.list_files("connections") == []

    def test_atomic_write_does_not_corrupt_on_failure(self, temp_storage):
        temp_storage.write_json("projects", "atomic", {"key": "value"})
        filepath = os.path.join(temp_storage.base_path, "projects", "atomic.json")
        assert os.path.exists(filepath)
        data = temp_storage.read_json("projects", "atomic")
        assert data == {"key": "value"}


# ======================================================================
# SerializationService
# ======================================================================

class TestSerializationService:
    def test_serialize_project(self):
        now = datetime(2026, 7, 18, 12, 0, 0)
        p = {"id": "test", "name": "Test", "description": "desc",
             "source": "/path", "created": now, "modified": now}
        data = serialize_project(p)
        assert data["name"] == "Test"
        assert data["created"] == "2026-07-18T12:00:00"

    def test_deserialize_project(self):
        data = {"id": "test", "name": "Test", "description": "desc",
                "source": "/path", "created": "2026-07-18T12:00:00",
                "modified": "2026-07-18T12:00:00"}
        p = deserialize_project(data)
        assert p["name"] == "Test"
        assert isinstance(p["created"], datetime)

    def test_serialize_deserialize_roundtrip(self):
        now = datetime.now()
        original = {"id": "x", "name": "X", "description": "desc",
                    "source": "/x", "created": now, "modified": now}
        data = serialize_project(original)
        restored = deserialize_project(data)
        assert restored["name"] == original["name"]
        assert restored["id"] == original["id"]

    def test_serialize_connection(self):
        now = datetime(2026, 7, 18, 12, 0, 0)
        c = {"id": "c1", "name": "Conn1", "conn_type": "local",
             "path": "/data", "favorite": True, "connected_at": now}
        data = serialize_connection(c)
        assert data["name"] == "Conn1"
        assert data["favorite"] is True
        assert "T12:00:00" in data["connected_at"]

    def test_deserialize_connection(self):
        data = {"id": "c1", "name": "Conn1", "conn_type": "local",
                "path": "/data", "favorite": True,
                "connected_at": "2026-07-18T12:00:00"}
        c = deserialize_connection(data)
        assert c["name"] == "Conn1"
        assert c["file_count"] == 0  # default

    def test_serialize_projects_list(self):
        now = datetime.now()
        projects = [{"id": "a", "name": "A", "created": now, "modified": now},
                    {"id": "b", "name": "B", "created": now, "modified": now}]
        data = serialize_projects(projects)
        assert len(data) == 2
        restored = deserialize_projects(data)
        assert len(restored) == 2

    def test_serialize_context(self):
        ctx_dict = {
            "current_project_id": "p1",
            "current_connection_id": "c1",
            "current_workspace": "processing",
            "navigation_history": ["home", "projects"],
            "theme": "dark",
            "sidebar_collapsed": True,
            "inspector_visible": False,
        }
        data = serialize_context(ctx_dict)
        assert data["theme"] == "dark"
        assert data["sidebar_collapsed"] is True

    def test_deserialize_context_defaults(self):
        data = {"current_workspace": "projects"}
        ctx = deserialize_context(data)
        assert ctx["current_workspace"] == "projects"
        assert ctx["theme"] == "light"  # default
        assert ctx["sidebar_collapsed"] is False  # default
        assert ctx["current_project_id"] is None  # default


# ======================================================================
# WorkspaceContext
# ======================================================================

class TestWorkspaceContext:
    def test_default_state(self):
        ctx = WorkspaceContext()
        assert ctx.current_workspace == "home"
        assert ctx.current_project_id is None
        assert ctx.current_connection_id is None
        assert ctx.theme == "light"
        assert ctx.sidebar_collapsed is False
        assert ctx.inspector_visible is True

    def test_workspace_change_tracks_history(self):
        ctx = WorkspaceContext()
        ctx.current_workspace = "projects"
        ctx.current_workspace = "connection"
        assert ctx.navigation_history == ["home", "projects"]
        assert ctx.current_workspace == "connection"

    def test_nav_back(self):
        ctx = WorkspaceContext()
        ctx.current_workspace = "a"
        ctx.current_workspace = "b"
        assert ctx.nav_back() == "a"
        assert ctx.nav_back() == "home"

    def test_nav_back_empty(self):
        ctx = WorkspaceContext()
        assert ctx.nav_back() is None

    def test_recent_projects(self):
        ctx = WorkspaceContext()
        ctx.add_recent_project("p1")
        ctx.add_recent_project("p2")
        ctx.add_recent_project("p1")  # duplicates move to front
        assert ctx.recent_projects == ["p1", "p2"]

    def test_recent_connections(self):
        ctx = WorkspaceContext()
        ctx.add_recent_connection("c1")
        ctx.add_recent_connection("c2")
        assert len(ctx.recent_connections) == 2

    def test_to_dict(self):
        ctx = WorkspaceContext()
        ctx.current_workspace = "processing"
        ctx.current_project_id = "p1"
        ctx.theme = "dark"
        d = ctx.to_dict()
        assert d["current_workspace"] == "processing"
        assert d["current_project_id"] == "p1"
        assert d["theme"] == "dark"
        assert "version" in d

    def test_from_dict(self):
        ctx = WorkspaceContext()
        ctx.from_dict({
            "current_workspace": "connection",
            "current_project_id": "p2",
            "theme": "dark",
            "sidebar_collapsed": True,
        })
        assert ctx.current_workspace == "connection"
        assert ctx.current_project_id == "p2"
        assert ctx.theme == "dark"
        assert ctx.sidebar_collapsed is True

    def test_reset(self):
        ctx = WorkspaceContext()
        ctx.current_workspace = "processing"
        ctx.current_project_id = "p1"
        ctx.theme = "dark"
        ctx.reset()
        assert ctx.current_workspace == "home"
        assert ctx.current_project_id is None
        assert ctx.theme == "light"

    def test_on_change_callback(self):
        ctx = WorkspaceContext()
        calls = []
        ctx.on_change(lambda: calls.append(1))
        ctx.current_workspace = "projects"
        assert len(calls) >= 1


# ======================================================================
# MigrationService
# ======================================================================

class TestMigrationService:
    def test_current_version(self, temp_storage):
        mig = MigrationService(temp_storage)
        assert mig.current_version() == CURRENT_STORAGE_VERSION

    def test_stored_version_fresh(self, temp_storage):
        mig = MigrationService(temp_storage)
        assert mig.stored_version() == 0

    def test_run_fresh_storage(self, temp_storage):
        mig = MigrationService(temp_storage)
        log = mig.run()
        assert isinstance(log, list)
        assert mig.stored_version() == CURRENT_STORAGE_VERSION

    def test_run_twice_no_duplicate(self, temp_storage):
        mig = MigrationService(temp_storage)
        mig.run()
        log = mig.run()
        assert log == []

    def test_metadata_written(self, temp_storage):
        mig = MigrationService(temp_storage)
        mig.run()
        meta = temp_storage.read_json("metadata", "version")
        assert meta is not None
        assert meta["storage_version"] == CURRENT_STORAGE_VERSION
        assert "application_version" in meta


# ======================================================================
# PersistenceService
# ======================================================================

class TestPersistenceService:
    def test_save_load_projects(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        projects = [
            {"id": "p1", "name": "Project 1", "created": datetime.now(), "modified": datetime.now()},
            {"id": "p2", "name": "Project 2", "created": datetime.now(), "modified": datetime.now()},
        ]
        ps.save_projects(projects)
        loaded = ps.load_projects()
        assert len(loaded) == 2
        assert loaded[0]["name"] == "Project 1"

    def test_save_load_connections(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        conns = [
            {"id": "c1", "name": "Conn 1", "conn_type": "local", "path": "/a"},
            {"id": "c2", "name": "Conn 2", "conn_type": "local", "path": "/b"},
        ]
        ps.save_connections(conns)
        loaded = ps.load_connections()
        assert len(loaded) == 2

    def test_save_individual_project(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.save_project({"id": "p1", "name": "P1", "created": datetime.now(), "modified": datetime.now()})
        ps.save_project({"id": "p2", "name": "P2", "created": datetime.now(), "modified": datetime.now()})
        loaded = ps.load_projects()
        assert len(loaded) == 2

    def test_delete_project(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.save_project({"id": "del", "name": "Delete Me", "created": datetime.now(), "modified": datetime.now()})
        assert ps.delete_project("del") is True
        assert len(ps.load_projects()) == 0

    def test_save_load_session(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ctx.current_workspace = "processing"
        ctx.current_project_id = "p1"
        ctx.theme = "dark"
        ps.save_session()
        loaded = ps.load_session()
        assert loaded is not None
        assert loaded["current_workspace"] == "processing"
        assert loaded["current_project_id"] == "p1"
        assert loaded["theme"] == "dark"

    def test_restore_session(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ctx.current_workspace = "connection"
        ctx.current_project_id = "p_restore"
        ps.save_session()

        ctx2 = WorkspaceContext()
        ps2 = PersistenceService(storage, MigrationService(storage), ctx2)
        ps2.run_migrations()
        result = ps2.restore_session()
        assert result is True
        assert ctx2.current_workspace == "connection"
        assert ctx2.current_project_id == "p_restore"

    def test_restore_no_session(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        result = ps.restore_session()
        assert result is False

    def test_create_backup(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.save_project({"id": "backup_test", "name": "BT", "created": datetime.now(), "modified": datetime.now()})
        backup_path = ps.create_backup("test_backup")
        assert os.path.isdir(backup_path)
        assert "test_backup" in backup_path

    def test_list_backups(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.create_backup("b1")
        ps.create_backup("b2")
        backups = ps.list_backups()
        assert len(backups) >= 2

    def test_restore_backup(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.save_project({"id": "original", "name": "Original", "created": datetime.now(), "modified": datetime.now()})
        backup_path = ps.create_backup("pre_clear")
        ps.clear_all()
        assert len(ps.load_projects()) == 0

        # Restore from backup
        backup_name = os.path.basename(backup_path)
        result = ps.restore_backup(backup_name)
        assert result is True
        loaded = ps.load_projects()
        assert len(loaded) >= 1

    def test_backup_restore_roundtrip(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.save_project({"id": "r1", "name": "Roundtrip", "created": datetime.now(), "modified": datetime.now()})
        ctx.current_workspace = "validation"
        ps.save_session()

        path = ps.create_backup("roundtrip")
        name = os.path.basename(path)
        ps.clear_all()
        ps.restore_backup(name)

        loaded_projects = ps.load_projects()
        assert any(p["name"] == "Roundtrip" for p in loaded_projects)

    def test_save_preferences(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        prefs = {"language": "en", "auto_save": True}
        ps.save_preferences(prefs)
        loaded = ps.load_preferences()
        assert loaded["language"] == "en"
        assert loaded["auto_save"] is True

    def test_project_persistence_through_service(self, temp_persistence):
        """Verify ProjectService persists through the full stack."""
        ps, ctx, storage = temp_persistence
        from ui.services.project_service import ProjectService
        psvc = ProjectService(ps, ctx)
        count_before = len(psvc.list_projects())
        psvc.create_project("Persistence Check", "Will it persist?", "/tmp")
        # Reload from persistence
        psvc2 = ProjectService(ps, ctx)
        assert len(psvc2.list_projects()) == count_before + 1
        names = [p["name"] for p in psvc2.list_projects()]
        assert "Persistence Check" in names

    def test_connection_persistence_through_service(self, temp_persistence):
        """Verify ConnectionService persists through the full stack."""
        ps, ctx, storage = temp_persistence
        from ui.services.connection_service import ConnectionService
        csvc = ConnectionService(ps, ctx)
        count_before = len(csvc.list_connections())
        csvc.add_connection("Persist Conn", "local", "/test", "Testing persistence")
        csvc2 = ConnectionService(ps, ctx)
        assert len(csvc2.list_connections()) == count_before + 1

    def test_corrupted_json_returns_default(self, temp_persistence):
        """StorageService handles corrupt JSON gracefully."""
        ps, ctx, storage = temp_persistence
        filepath = os.path.join(storage.base_path, "projects", "corrupt.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write("not valid json{{{")
        data = storage.read_json("projects", "corrupt", default=[])
        assert data == []

    def test_missing_file_returns_default(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        data = storage.read_json("projects", "nonexistent_file_xyz", default="default_val")
        assert data == "default_val"

    def test_run_migrations(self, temp_persistence):
        ps, ctx, storage = temp_persistence
        ps.run_migrations()
        assert ps.storage_version() == CURRENT_STORAGE_VERSION

    def test_shared_module_imports(self):
        """Verify shared module can be imported without errors."""
        import importlib
        import ui.shared
        importlib.reload(ui.shared)
        assert hasattr(ui.shared, "init_all")
        assert hasattr(ui.shared, "context")
        assert hasattr(ui.shared, "project_svc")
