"""Tests — Flush Layer: Engine."""

import pytest
import os
import tempfile

from dav_platform.core.contracts import (
    ExecutionMetadata,
    ExecutionResult,
    ExecutionState,
    ExecutionStepResult,
    FlushConfig,
    FlushResult,
    OutputArtifacts,
    ExportManifest,
)
from dav_platform.flush.engine import FlushEngine


class TestFlushEngine:
    def test_default_config(self):
        engine = FlushEngine()
        assert engine.config is not None

    def test_flush_basic(self):
        engine = FlushEngine()
        result = engine.flush()
        assert isinstance(result, FlushResult)
        assert result.success is True
        assert result.cleanup is not None
        assert result.metrics is not None
        assert result.summary is not None

    def test_flush_with_execution_result(self):
        engine = FlushEngine()
        exec_result = ExecutionResult(
            state=ExecutionState.COMPLETED,
            metadata=ExecutionMetadata(workflow="test", total_steps=3, completed_steps=3, outcome="success"),
        )
        result = engine.flush(execution_result=exec_result)
        assert result.success is True
        assert result.summary.execution_status == "success"

    def test_flush_with_failed_execution(self):
        engine = FlushEngine()
        exec_result = ExecutionResult(state=ExecutionState.FAILED, errors=["Something broke"])
        result = engine.flush(execution_result=exec_result)
        assert result.summary.execution_status == "failed"

    def test_flush_with_output_artifacts(self):
        engine = FlushEngine()
        artifacts = OutputArtifacts(
            excel_files=["/tmp/report.xlsx"],
            csv_files=["/tmp/data.csv"],
        )
        manifest = ExportManifest(total_files=2)
        result = engine.flush(output_artifacts=artifacts, export_manifest=manifest)
        assert result.metrics.export_count > 0

    def test_flush_with_manifest(self):
        engine = FlushEngine()
        manifest = ExportManifest(total_files=5)
        result = engine.flush(export_manifest=manifest)
        assert result.metrics.export_count >= 5

    def test_flush_dry_run(self):
        config = FlushConfig(dry_run=True)
        engine = FlushEngine(config=config)
        result = engine.flush()
        assert result.success is True

    def test_flush_cleans_temp_files(self):
        config = FlushConfig(dry_run=False)
        engine = FlushEngine(config=config)
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as f:
            path = f.name
        engine.cleanup.register_temp_file(path)
        result = engine.flush()
        assert result.cleanup.files_deleted >= 1
        assert not os.path.exists(path)

    def test_flush_retains_temp_files_when_configured(self):
        config = FlushConfig(retain_temp_files=True, temp_directories=["/keep"])
        engine = FlushEngine(config=config)
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as f:
            path = f.name
        engine.cleanup.register_temp_file(path)
        result = engine.flush()
        self.add_cleanup = lambda: None
        if os.path.exists(path):
            os.unlink(path)

    def test_flush_connections(self):
        engine = FlushEngine()
        closed = []
        class FakeHandle:
            def close(self):
                closed.append(True)
        engine.connections.register({"type": "ssh", "handle": FakeHandle()})
        result = engine.flush()
        assert result.cleanup.connections_closed >= 1

    def test_flush_caches(self):
        engine = FlushEngine()
        engine.cache.register("test", {"a": 1})
        result = engine.flush()
        assert result.cleanup.caches_cleared >= 1

    def test_flush_sessions(self):
        engine = FlushEngine()
        engine.session.register_tracker({"p": 1})
        engine.session.register_context({"s": "running"})
        result = engine.flush()
        assert result.cleanup.sessions_reset == 2

    def test_get_audit_trail(self):
        engine = FlushEngine()
        engine.flush()
        audit = engine.get_audit_trail()
        assert audit["entry_count"] >= 1

    def test_flush_with_warnings_and_errors(self):
        engine = FlushEngine()
        exec_result = ExecutionResult(
            state=ExecutionState.COMPLETED,
            warnings=["Low memory"],
            errors=[],
        )
        result = engine.flush(execution_result=exec_result)
        assert result.summary is not None

    def test_flush_delete_exports(self):
        config = FlushConfig(delete_exports=True)
        engine = FlushEngine(config=config)
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        engine.cleanup.delete_exports = lambda dry_run=False: {"files_deleted": 1}
        result = engine.flush()
        assert result.success is True

    def test_flush_metrics_collected(self):
        engine = FlushEngine()
        engine.metrics.add_rows_processed(500)
        engine.metrics.add_files_processed(10)
        result = engine.flush()
        assert result.metrics.rows_processed == 500
        assert result.metrics.files_processed == 10

    def test_flush_lifecycle_summary(self):
        engine = FlushEngine()
        artifacts = OutputArtifacts(excel_files=["/tmp/r.xlsx"])
        result = engine.flush(output_artifacts=artifacts)
        assert "/tmp/r.xlsx" in result.summary.generated_outputs
