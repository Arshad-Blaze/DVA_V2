"""Tests — Flush Layer: Cleanup, Resources, Connections, Cache, Session, Metrics, Audit, Summary."""

import pytest
import tempfile
import os

from dav_platform.flush.cleanup import CleanupManager
from dav_platform.flush.resources import ResourceManager
from dav_platform.flush.connections import ConnectionCleanup
from dav_platform.flush.cache import CacheManager
from dav_platform.flush.session import SessionCleanup
from dav_platform.flush.metrics import MetricsCollector
from dav_platform.flush.audit import AuditTrail
from dav_platform.flush.summary import LifecycleSummaryBuilder
from dav_platform.core.contracts import (
    CleanupSummary,
    ExecutionMetrics,
    OutputArtifacts,
)


# ---------------------------------------------------------------------------
# Test CleanupManager
# ---------------------------------------------------------------------------
class TestCleanupManager:
    def test_delete_temp_files(self):
        cm = CleanupManager()
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as f:
            path = f.name
        assert os.path.exists(path)
        cm.register_temp_file(path)
        result = cm.delete_temp_files()
        assert result["files_deleted"] == 1
        assert not os.path.exists(path)

    def test_delete_temp_dirs(self):
        cm = CleanupManager()
        tmpdir = tempfile.mkdtemp()
        assert os.path.isdir(tmpdir)
        cm.register_temp_dir(tmpdir)
        result = cm.delete_temp_dirs()
        assert result["dirs_deleted"] == 1
        assert not os.path.isdir(tmpdir)

    def test_delete_temp_files_dry_run(self):
        cm = CleanupManager()
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as f:
            path = f.name
        cm.register_temp_file(path)
        result = cm.delete_temp_files(dry_run=True)
        assert result["dry_run"] is True
        assert os.path.exists(path)
        os.unlink(path)

    def test_retain_specific_files(self):
        cm = CleanupManager()
        with tempfile.NamedTemporaryFile(suffix=".a", delete=False) as fa:
            path_a = fa.name
        with tempfile.NamedTemporaryFile(suffix=".b", delete=False) as fb:
            path_b = fb.name
        cm.register_temp_file(path_a)
        cm.register_temp_file(path_b)
        result = cm.delete_temp_files(retain=[path_a])
        assert result["files_deleted"] == 1
        assert os.path.exists(path_a)
        assert not os.path.exists(path_b)
        os.unlink(path_a)

    def test_delete_exports(self):
        cm = CleanupManager()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        result = cm.delete_exports(export_files=[path])
        assert result["files_deleted"] == 1

    def test_count_properties(self):
        cm = CleanupManager()
        assert cm.temp_file_count == 0
        assert cm.temp_dir_count == 0
        cm.register_temp_file("/tmp/a")
        cm.register_temp_dir("/tmp/d")
        assert cm.temp_file_count == 1
        assert cm.temp_dir_count == 1


# ---------------------------------------------------------------------------
# Test ResourceManager
# ---------------------------------------------------------------------------
class TestResourceManager:
    def test_cleanup_memory(self):
        rm = ResourceManager()
        result = rm.cleanup_memory()
        assert result["status"] == "completed"

    def test_cleanup_memory_dry_run(self):
        rm = ResourceManager()
        result = rm.cleanup_memory(dry_run=True)
        assert result["dry_run"] is True

    def test_cleanup_buffers(self):
        rm = ResourceManager()
        buffers = [1, 2, 3]
        result = rm.cleanup_buffers(buffers)
        assert result["status"] == "completed"
        assert len(buffers) == 0

    def test_cleanup_buffers_dry_run(self):
        rm = ResourceManager()
        buffers = [1, 2, 3]
        result = rm.cleanup_buffers(buffers, dry_run=True)
        assert result["dry_run"] is True
        assert len(buffers) == 3

    def test_cleanup_dataframes(self):
        rm = ResourceManager()
        dfs = ["df1", "df2"]
        result = rm.cleanup_dataframes(dfs)
        assert result["dataframes_dropped"] == 2
        assert len(dfs) == 0


# ---------------------------------------------------------------------------
# Test ConnectionCleanup
# ---------------------------------------------------------------------------
class TestConnectionCleanup:
    def test_close_all(self):
        cc = ConnectionCleanup()
        closed = []
        class FakeHandle:
            def close(self):
                closed.append(True)
        cc.register({"type": "ssh", "handle": FakeHandle()})
        cc.register({"type": "mft", "handle": FakeHandle()})
        result = cc.close_all()
        assert result["connections_closed"] == 2
        assert len(closed) == 2

    def test_close_all_dry_run(self):
        cc = ConnectionCleanup()
        cc.register({"type": "ssh", "handle": object()})
        result = cc.close_all(dry_run=True)
        assert result["dry_run"] is True
        assert cc.count == 1

    def test_close_without_handle(self):
        cc = ConnectionCleanup()
        cc.register({"type": "ssh"})
        result = cc.close_all()
        assert result["connections_closed"] == 1

    def test_count(self):
        cc = ConnectionCleanup()
        assert cc.count == 0
        cc.register({"type": "ssh"})
        assert cc.count == 1


# ---------------------------------------------------------------------------
# Test CacheManager
# ---------------------------------------------------------------------------
class TestCacheManager:
    def test_clear_all(self):
        cm = CacheManager()
        d = {"a": 1}
        cm.register("test", d)
        result = cm.clear_all()
        assert result["caches_cleared"] >= 1
        assert cm.cache_count == 0

    def test_clear_all_preserve(self):
        cm = CacheManager()
        d1 = {"a": 1}
        d2 = {"b": 2}
        cm.register("keep", d1)
        cm.register("delete", d2)
        result = cm.clear_all(preserve=["keep"])
        assert result["caches_cleared"] >= 1

    def test_clear_all_dry_run(self):
        cm = CacheManager()
        cm.register("test", {})
        result = cm.clear_all(dry_run=True)
        assert result["dry_run"] is True
        assert cm.cache_count == 1

    def test_clear_key(self):
        cm = CacheManager()
        cm.register("test", {})
        assert cm.clear_key("test") is True
        assert cm.clear_key("nonexistent") is False

    def test_cache_count(self):
        cm = CacheManager()
        assert cm.cache_count == 0
        cm.register("a", {})
        assert cm.cache_count == 1


# ---------------------------------------------------------------------------
# Test SessionCleanup
# ---------------------------------------------------------------------------
class TestSessionCleanup:
    def test_reset_all(self):
        sc = SessionCleanup()
        tracker = {"progress": 50}
        ctx = {"state": "running"}
        sc.register_tracker(tracker)
        sc.register_context(ctx)
        result = sc.reset_all()
        assert result["trackers_reset"] == 1
        assert result["contexts_reset"] == 1
        assert len(tracker) == 0
        assert len(ctx) == 0

    def test_reset_all_dry_run(self):
        sc = SessionCleanup()
        sc.register_tracker({"p": 1})
        result = sc.reset_all(dry_run=True)
        assert result["dry_run"] is True


# ---------------------------------------------------------------------------
# Test MetricsCollector
# ---------------------------------------------------------------------------
class TestMetricsCollector:
    def test_build_defaults(self):
        mc = MetricsCollector()
        metrics = mc.build()
        assert isinstance(metrics, ExecutionMetrics)
        assert metrics.rows_processed == 0
        assert metrics.success_rate == 100.0

    def test_record_layer_time(self):
        mc = MetricsCollector()
        mc.record_layer_time("detection", 1.5)
        mc.record_layer_time("canonical", 2.0)
        metrics = mc.build()
        assert metrics.layer_timings["detection"] == 1.5
        assert metrics.layer_timings["canonical"] == 2.0

    def test_add_rows(self):
        mc = MetricsCollector()
        mc.add_rows_processed(100)
        mc.add_rows_processed(50)
        assert mc.build().rows_processed == 150

    def test_add_files(self):
        mc = MetricsCollector()
        mc.add_files_processed()
        mc.add_files_processed(2)
        assert mc.build().files_processed == 3

    def test_add_chunks_and_exports(self):
        mc = MetricsCollector()
        mc.add_chunks(5)
        mc.add_exports(3)
        metrics = mc.build()
        assert metrics.chunk_count == 5
        assert metrics.export_count == 3

    def test_validation_results(self):
        mc = MetricsCollector()
        mc.set_validation_results(10, 2)
        metrics = mc.build()
        assert metrics.validation_rules_passed == 10
        assert metrics.validation_rules_failed == 2
        assert metrics.success_rate == 83.33333333333334

    def test_retries(self):
        mc = MetricsCollector()
        mc.add_retries(3)
        assert mc.build().retry_count == 3

    def test_memory(self):
        mc = MetricsCollector()
        mc.record_memory(100.0, 200.0)
        metrics = mc.build()
        assert metrics.memory_usage_mb == 100.0
        assert metrics.peak_memory_mb == 200.0


# ---------------------------------------------------------------------------
# Test AuditTrail
# ---------------------------------------------------------------------------
class TestAuditTrail:
    def test_empty_audit(self):
        audit = AuditTrail()
        result = audit.build()
        assert result["entry_count"] == 0

    def test_record(self):
        audit = AuditTrail()
        audit.record({"type": "test", "message": "hello"})
        result = audit.build()
        assert result["entry_count"] == 1
        assert result["entries"][0]["message"] == "hello"

    def test_record_layer(self):
        audit = AuditTrail()
        audit.record_layer("detection", "passed", 1.5)
        result = audit.build()
        assert result["entry_count"] == 1
        assert result["entries"][0]["layer"] == "detection"

    def test_record_cleanup(self):
        audit = AuditTrail()
        audit.record_cleanup("files", "completed", {"deleted": 5})
        result = audit.build()
        assert result["entries"][0]["action"] == "files"

    def test_record_error(self):
        audit = AuditTrail()
        audit.record_error("processing", "timeout")
        result = audit.build()
        assert result["entries"][0]["type"] == "error"

    def test_start_end(self):
        audit = AuditTrail()
        audit.start()
        audit.end()
        result = audit.build()
        assert result["start_time"] != ""
        assert result["end_time"] != ""

    def test_execution_id(self):
        audit = AuditTrail()
        audit.set_execution_id("exec-123")
        assert audit.build()["execution_id"] == "exec-123"


# ---------------------------------------------------------------------------
# Test LifecycleSummaryBuilder
# ---------------------------------------------------------------------------
class TestLifecycleSummaryBuilder:
    def test_build_basic(self):
        builder = LifecycleSummaryBuilder()
        summary = builder.build(execution_status="success", total_duration=1.5)
        assert summary.execution_status == "success"
        assert summary.total_duration_seconds == 1.5
        assert summary.cleanup_status == "skipped"

    def test_build_with_errors(self):
        builder = LifecycleSummaryBuilder()
        csum = CleanupSummary(errors=["File not found"])
        summary = builder.build(
            execution_status="failed", total_duration=2.0,
            cleanup_summary=csum,
            errors=["Something failed"],
        )
        assert summary.execution_status == "failed"
        assert len(summary.errors) == 1
        assert summary.cleanup_status == "partial"

    def test_build_with_artifacts(self):
        builder = LifecycleSummaryBuilder()
        artifacts = OutputArtifacts(
            excel_files=["/tmp/report.xlsx"],
            csv_files=["/tmp/data.csv"],
        )
        summary = builder.build(
            execution_status="success", total_duration=1.0,
            artifacts=artifacts,
        )
        assert len(summary.generated_outputs) == 2
