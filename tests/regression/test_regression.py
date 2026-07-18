"""Regression tests — frozen contract and architecture integrity.

These tests ensure no regressions are reintroduced after fixes.
Run as part of the full regression suite.
"""

import importlib
import ast
import os
from pathlib import Path


# ============================================================================
# CONTRACT REGRESSION: Core exports must be complete
# ============================================================================

class TestCoreExportsComplete:
    """Verify dav_platform.core exports all critical types."""

    def test_core_exports_connection_types(self):
        from dav_platform.core import IDataSource, DataSourceEntry, DataSourceError, DirectorySummary
        assert IDataSource is not None
        assert DataSourceEntry is not None
        assert DataSourceError is not None
        assert DirectorySummary is not None

    def test_core_exports_detection_types(self):
        from dav_platform.core import (
            DiscoveryResult, FileType, EncodingType, RecordTypeInfo,
            LayoutField, ExcelSheetInfo, DetectionStatistics,
            CandidateMapping, QuantityRecommendation,
        )
        assert all(t is not None for t in [
            DiscoveryResult, FileType, EncodingType, RecordTypeInfo,
            LayoutField, ExcelSheetInfo, DetectionStatistics,
            CandidateMapping, QuantityRecommendation,
        ])

    def test_core_exports_canonical_types(self):
        from dav_platform.core import CanonicalDataset, CanonicalMetadata, ColumnMapping, CANONICAL_COLUMNS
        assert CanonicalDataset is not None
        assert CanonicalMetadata is not None
        assert ColumnMapping is not None
        assert isinstance(CANONICAL_COLUMNS, dict)

    def test_core_exports_requirement_types(self):
        from dav_platform.core import OperationContext, ProcessingMode, BusinessGoal, CapabilityMatrix, ExecutionStep
        assert all(t is not None for t in [
            OperationContext, ProcessingMode, BusinessGoal, CapabilityMatrix, ExecutionStep,
        ])

    def test_core_exports_operation_types(self):
        from dav_platform.core import (
            ExecutionState, ExecutionStepResult, OperationLog,
            ExecutionMetadata, ExecutionResult,
        )
        assert all(t is not None for t in [
            ExecutionState, ExecutionStepResult, OperationLog,
            ExecutionMetadata, ExecutionResult,
        ])

    def test_core_exports_shared_types(self):
        from dav_platform.core import (
            ProcessingResult, ValidationResult, ValidationIssue,
            ValidationSeverity, ReportFormat, ReportOutput,
        )
        assert all(t is not None for t in [
            ProcessingResult, ValidationResult, ValidationIssue,
            ValidationSeverity, ReportFormat, ReportOutput,
        ])


# ============================================================================
# CONTRACT REGRESSION: No naming collisions between ValidationResult classes
# ============================================================================

class TestValidationResultNoCollision:
    """Verify canonical and requirements ValidationResults don't shadow core."""

    def test_canonical_validation_result_is_distinct(self):
        from dav_platform.canonical.validation import CanonicalValidationResult
        from dav_platform.core.contracts import ValidationResult
        assert CanonicalValidationResult is not ValidationResult

    def test_requirements_validation_result_is_distinct(self):
        from dav_platform.requirements.validator import ModeValidationResult
        from dav_platform.core.contracts import ValidationResult
        assert ModeValidationResult is not ValidationResult

    def test_canonical_and_requirements_are_distinct(self):
        from dav_platform.canonical.validation import CanonicalValidationResult
        from dav_platform.requirements.validator import ModeValidationResult
        assert CanonicalValidationResult is not ModeValidationResult

    def test_canonical_validation_result_has_required_fields(self):
        from dav_platform.canonical.validation import CanonicalValidationResult
        r = CanonicalValidationResult()
        assert hasattr(r, 'passed')
        assert hasattr(r, 'issues')
        assert hasattr(r, 'warnings')
        assert hasattr(r, 'checked_columns')
        assert hasattr(r, 'total_rows')

    def test_mode_validation_result_has_required_fields(self):
        from dav_platform.requirements.validator import ModeValidationResult
        r = ModeValidationResult()
        assert hasattr(r, 'passed')
        assert hasattr(r, 'issues')
        assert hasattr(r, 'warnings')


# ============================================================================
# ARCHITECTURE REGRESSION: Frozen layers don't import from operations/
# ============================================================================

class TestFrozenLayerIsolation:
    """Verify frozen layers don't import from operations/."""

    LAYERS_TO_CHECK = [
        "dav_platform/connection",
        "dav_platform/detection",
        "dav_platform/canonical",
        "dav_platform/requirements",
    ]

    def _get_imports_from_file(self, filepath):
        """Extract all import statements from a Python file using AST."""
        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read())
        except (SyntaxError, FileNotFoundError):
            return []

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _scan_layer_for_operations_imports(self, layer_path):
        """Scan all .py files in a layer for imports from operations/."""
        violations = []
        root = Path(layer_path)
        if not root.exists():
            return violations

        for py_file in root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            imports = self._get_imports_from_file(str(py_file))
            for imp in imports:
                if imp.startswith("dav_platform.operations"):
                    violations.append(f"{py_file}: imports {imp}")
        return violations

    def test_connection_no_operations_imports(self):
        violations = self._scan_layer_for_operations_imports("dav_platform/connection")
        assert violations == [], f"Connection layer has operations imports: {violations}"

    def test_detection_no_operations_imports(self):
        violations = self._scan_layer_for_operations_imports("dav_platform/detection")
        assert violations == [], f"Detection layer has operations imports: {violations}"

    def test_canonical_no_operations_imports(self):
        violations = self._scan_layer_for_operations_imports("dav_platform/canonical")
        assert violations == [], f"Canonical layer has operations imports: {violations}"

    def test_requirements_no_operations_imports(self):
        violations = self._scan_layer_for_operations_imports("dav_platform/requirements")
        assert violations == [], f"Requirements layer has operations imports: {violations}"


# ============================================================================
# ARCHITECTURE REGRESSION: No circular dependencies
# ============================================================================

class TestNoCircularDependencies:
    """Verify no circular import chains exist."""

    def test_operations_imports_only_core(self):
        """operations/ should only import from core/ and itself."""
        violations = []
        root = Path("dav_platform/operations")
        for py_file in root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                with open(py_file, 'r') as f:
                    tree = ast.parse(f.read())
            except (SyntaxError, FileNotFoundError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("dav_platform.") and not node.module.startswith("dav_platform.core") and not node.module.startswith("dav_platform.operations"):
                        violations.append(f"{py_file}: imports {node.module}")
        assert violations == [], f"Operations layer has illegal imports: {violations}"


# ============================================================================
# CONTRACT REGRESSION: Key contract field access
# ============================================================================

class TestContractFieldAccess:
    """Verify critical contract fields are accessible and correct."""

    def test_execution_result_properties(self):
        from dav_platform.core.contracts import ExecutionResult, ExecutionState
        r = ExecutionResult(state=ExecutionState.COMPLETED)
        assert r.succeeded is True
        assert r.failed is False
        assert r.cancelled is False

    def test_execution_result_failed_state(self):
        from dav_platform.core.contracts import ExecutionResult, ExecutionState
        r = ExecutionResult(state=ExecutionState.FAILED)
        assert r.succeeded is False
        assert r.failed is True
        assert r.cancelled is False

    def test_execution_result_cancelled_state(self):
        from dav_platform.core.contracts import ExecutionResult, ExecutionState
        r = ExecutionResult(state=ExecutionState.CANCELLED)
        assert r.succeeded is False
        assert r.failed is False
        assert r.cancelled is True

    def test_canonical_dataset_row_count(self):
        import polars as pl
        from dav_platform.core.contracts import CanonicalDataset, CanonicalMetadata
        ds = CanonicalDataset(
            file_path="/test.csv",
            canonical_columns=["store"],
            metadata=CanonicalMetadata(total_rows=5),
            dataframe=pl.DataFrame({"store": ["1", "2", "3", "4", "5"]}),
        )
        assert ds.row_count == 5
        assert ds.column_count == 1

    def test_operation_context_execution_plan(self):
        from dav_platform.core.contracts import OperationContext, ExecutionStep
        ctx = OperationContext(
            execution_plan=[
                ExecutionStep(step_number=1, action="load", description="Load"),
                ExecutionStep(step_number=2, action="preview", description="Preview"),
            ]
        )
        assert len(ctx.execution_plan) == 2
        assert ctx.execution_plan[0].action == "load"
