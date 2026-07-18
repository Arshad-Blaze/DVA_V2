"""Integration Tests — Output → Flush."""

import tempfile
import os
import polars as pl

from dav_platform.core.contracts import (
    ExecutionMetadata,
    ExecutionResult,
    ExecutionState,
    OutputConfig,
    ValidationResult,
    ValidationStatistics,
    ValidationReportData,
    ExportManifest,
)
from dav_platform.output.engine import OutputEngine
from dav_platform.flush.engine import FlushEngine


def _make_validation_data():
    stats = ValidationStatistics(total_rules_evaluated=5, rules_passed=5)
    return ValidationReportData(passed=True, total_checks=5, passed_checks=5, statistics=stats)


class TestOutputToFlushIntegration:
    def test_generate_then_flush(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(_make_validation_data())

            flush_engine = FlushEngine()
            result = flush_engine.flush(
                output_artifacts=artifacts,
                export_manifest=artifacts.manifest,
            )
            assert result.success is True
            assert result.cleanup is not None
            assert result.metrics is not None
            assert result.summary is not None
            assert result.summary.execution_status == "success"
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_generate_then_flush_with_execution_metadata(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(_make_validation_data())

            exec_result = ExecutionResult(
                state=ExecutionState.COMPLETED,
                metadata=ExecutionMetadata(
                    workflow="full_pipeline", total_steps=4, completed_steps=4, outcome="success"
                ),
            )
            flush_engine = FlushEngine()
            result = flush_engine.flush(
                execution_result=exec_result,
                output_artifacts=artifacts,
                export_manifest=artifacts.manifest,
            )
            assert result.success is True
            assert result.summary.execution_status == "success"
            assert len(result.summary.generated_outputs) >= 1
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_flush_after_failed_execution(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(_make_validation_data())

            exec_result = ExecutionResult(
                state=ExecutionState.FAILED,
                errors=["Processing pipeline crashed"],
            )
            flush_engine = FlushEngine()
            result = flush_engine.flush(
                execution_result=exec_result,
                output_artifacts=artifacts,
            )
            assert result.summary.execution_status == "failed"
            assert result.cleanup is not None
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_flush_dry_run_after_output(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(_make_validation_data())
            manifest = ExportManifest(total_files=3)

            from dav_platform.core.contracts import FlushConfig
            flush_config = FlushConfig(dry_run=True)
            flush_engine = FlushEngine(config=flush_config)
            result = flush_engine.flush(
                output_artifacts=artifacts,
                export_manifest=manifest,
            )
            assert result.success is True
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_full_pipeline_audit_trail(self):
        tmpdir = tempfile.mkdtemp()
        try:
            config = OutputConfig(output_dir=tmpdir)
            out_engine = OutputEngine(config)
            artifacts = out_engine.generate(_make_validation_data())

            flush_engine = FlushEngine()
            flush_engine.flush(
                output_artifacts=artifacts,
                export_manifest=artifacts.manifest,
            )
            audit = flush_engine.get_audit_trail()
            assert audit["entry_count"] >= 1
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
