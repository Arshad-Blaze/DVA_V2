import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3] / "dav_platform"

FROZEN_LAYERS = [
    ROOT / "connection",
    ROOT / "detection",
    ROOT / "canonical",
    ROOT / "requirements",
    ROOT / "operations",
    ROOT / "processing",
    ROOT / "validation",
    ROOT / "output",
    ROOT / "flush",
]

ALL_LAYERS = {
    "operations": ROOT / "operations",
    "requirements": ROOT / "requirements",
    "canonical": ROOT / "canonical",
    "detection": ROOT / "detection",
    "connection": ROOT / "connection",
    "processing": ROOT / "processing",
    "validation": ROOT / "validation",
    "output": ROOT / "output",
    "flush": ROOT / "flush",
    "core": ROOT / "core",
}

IMPORT_RULES: dict[str, list[str]] = {
    "operations": ["core", "operations"],
    "requirements": ["core", "canonical", "requirements"],
    "canonical": ["core", "canonical"],
    "detection": ["core", "detection"],
    "connection": ["core", "connection"],
    "processing": ["core", "processing"],
    "validation": ["core", "validation"],
    "output": ["core", "output"],
    "flush": ["core", "flush"],
}

BYPASS_RULES: dict[str, list[str]] = {
    "operations": ["detection", "connection"],
    "requirements": ["operations"],
    "canonical": ["operations", "requirements"],
    "processing": ["operations", "requirements", "canonical", "detection", "connection"],
    "validation": ["operations", "requirements", "canonical", "detection", "connection", "processing"],
    "output": ["operations", "requirements", "canonical", "detection", "connection", "processing", "validation"],
    "flush": ["operations", "requirements", "canonical", "detection", "connection", "processing", "validation", "output"],
}

OPERATIONS_KEYWORDS = [
    "group_by",
    "pivot",
    "business_rule",
    ".aggregate(",
    ".groupby(",
    ".sum(axis",
    ".count(axis",
]

UI_KEYWORDS = [
    "import tkinter",
    "import flask",
    "import django",
    "import streamlit",
    "import gradio",
    "import fastapi",
]

RETAILER_KEYWORDS = [
    "walmart",
    "costco",
    "kroger",
    "safeway",
    "albertsons",
    "publix",
    "h-e-b",
    "h_eb",
    "target_store",
    "wmt_",
    "tgt_",
    "cost_",
]


def _get_imports_from_file(filepath: str) -> list[str]:
    """Extract all imported module names from a Python file using AST."""
    try:
        tree = ast.parse(Path(filepath).read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                modules.append(node.module)
    return modules


def _py_files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.py"))


def _get_layer_from_import(mod: str) -> str | None:
    """Return the top-level dav_platform subpackage an import belongs to, or None."""
    parts = mod.split(".")
    if parts and parts[0] == "dav_platform" and len(parts) > 1:
        return parts[1]
    return None


# ---------------------------------------------------------------------------
# 1. TestFrozenLayerIsolation
# ---------------------------------------------------------------------------
class TestFrozenLayerIsolation:
    """Frozen layers must never import from dav_platform.operations."""

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_connection_does_not_import_operations(self):
        for f in _py_files(ALL_LAYERS["connection"]):
            for mod in _get_imports_from_file(str(f)):
                if _get_layer_from_import(mod) == "operations":
                    pytest.fail(f"{f} imports from operations: {mod}")

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_detection_does_not_import_operations(self):
        for f in _py_files(ALL_LAYERS["detection"]):
            for mod in _get_imports_from_file(str(f)):
                if _get_layer_from_import(mod) == "operations":
                    pytest.fail(f"{f} imports from operations: {mod}")

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_canonical_does_not_import_operations(self):
        for f in _py_files(ALL_LAYERS["canonical"]):
            for mod in _get_imports_from_file(str(f)):
                if _get_layer_from_import(mod) == "operations":
                    pytest.fail(f"{f} imports from operations: {mod}")

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_requirements_does_not_import_operations(self):
        for f in _py_files(ALL_LAYERS["requirements"]):
            for mod in _get_imports_from_file(str(f)):
                if _get_layer_from_import(mod) == "operations":
                    pytest.fail(f"{f} imports from operations: {mod}")


# ---------------------------------------------------------------------------
# 2. TestNoCircularDependencies
# ---------------------------------------------------------------------------
class TestNoCircularDependencies:
    """Each layer may only import from its allowed set of dependencies."""

    @pytest.mark.architecture
    @pytest.mark.regression
    @pytest.mark.parametrize("layer", list(IMPORT_RULES.keys()))
    def test_layer_respects_import_rules(self, layer: str):
        allowed = IMPORT_RULES[layer]
        layer_dir = ALL_LAYERS[layer]
        for f in _py_files(layer_dir):
            for mod in _get_imports_from_file(str(f)):
                dep_layer = _get_layer_from_import(mod)
                if dep_layer is not None and dep_layer not in allowed:
                    pytest.fail(
                        f"{f} [{layer}] imports '{mod}' "
                        f"which belongs to layer '{dep_layer}'; "
                        f"allowed layers: {allowed}"
                    )


# ---------------------------------------------------------------------------
# 3. TestNoLayerBypasses
# ---------------------------------------------------------------------------
class TestNoLayerBypasses:
    """Certain cross-layer imports are forbidden to prevent bypassing the
    dependency hierarchy."""

    @pytest.mark.architecture
    @pytest.mark.regression
    @pytest.mark.parametrize("layer", list(BYPASS_RULES.keys()))
    def test_layer_has_no_bypass_imports(self, layer: str):
        forbidden = BYPASS_RULES[layer]
        layer_dir = ALL_LAYERS[layer]
        for f in _py_files(layer_dir):
            for mod in _get_imports_from_file(str(f)):
                dep_layer = _get_layer_from_import(mod)
                if dep_layer in forbidden:
                    pytest.fail(
                        f"{f} [{layer}] bypasses into forbidden "
                        f"layer '{dep_layer}' via import '{mod}'"
                    )


# ---------------------------------------------------------------------------
# 4. TestNoBusinessLogicInOperations
# ---------------------------------------------------------------------------
class TestNoBusinessLogicInOperations:
    """Operations must be pure orchestration — no business logic keywords."""

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_operations_contains_no_business_keywords(self):
        violations: list[tuple[Path, str, str]] = []
        for f in _py_files(ALL_LAYERS["operations"]):
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for kw in OPERATIONS_KEYWORDS:
                    if kw in stripped:
                        violations.append((f, kw, stripped))
        if violations:
            msg_lines = ["Business logic keywords found in operations/:"]
            for fp, kw, src in violations:
                msg_lines.append(f"  {fp} -> keyword '{kw}' in: {src}")
            pytest.fail("\n".join(msg_lines))


# ---------------------------------------------------------------------------
# 5. TestNoUIImports
# ---------------------------------------------------------------------------
class TestNoUIImports:
    """Core platform modules must not import UI frameworks."""

    @pytest.mark.architecture
    @pytest.mark.regression
    def test_no_ui_framework_imports(self):
        violations: list[tuple[Path, str, str]] = []
        for layer_dir in ALL_LAYERS.values():
            if not layer_dir.is_dir():
                continue
            for f in _py_files(layer_dir):
                try:
                    lines = f.read_text(encoding="utf-8").splitlines()
                except UnicodeDecodeError:
                    continue
                for lineno, line in enumerate(lines, start=1):
                    stripped = line.strip()
                    for kw in UI_KEYWORDS:
                        if kw in stripped:
                            violations.append((f, kw, stripped))
        if violations:
            msg_lines = ["UI framework imports found in dav_platform/:"]
            for fp, kw, src in violations:
                msg_lines.append(f"  {fp} -> '{kw}' in: {src}")
            pytest.fail("\n".join(msg_lines))


# ---------------------------------------------------------------------------
# 6. TestNoRetailerSpecificLogic
# ---------------------------------------------------------------------------
class TestNoRetailerSpecificLogic:
    """operations/ and requirements/ must remain retailer-agnostic."""

    @pytest.mark.architecture
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "layer_key", ["operations", "requirements", "processing", "validation", "output", "flush"]
    )
    def test_no_retailer_names(self, layer_key: str):
        layer_dir = ALL_LAYERS[layer_key]
        violations: list[tuple[Path, str, str]] = []
        for f in _py_files(layer_dir):
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                lower = stripped.lower()
                for kw in RETAILER_KEYWORDS:
                    if kw in lower:
                        violations.append((f, kw, stripped))
        if violations:
            msg_lines = [f"Retailer-specific logic found in {layer_key}/:"]
            for fp, kw, src in violations:
                msg_lines.append(f"  {fp} -> keyword '{kw}' in: {src}")
            pytest.fail("\n".join(msg_lines))


# ---------------------------------------------------------------------------
# 7. TestSRPIntact
# ---------------------------------------------------------------------------
class TestSRPIntact:
    """Each layer must have exactly one entry-point module and no
    'god modules' exceeding 500 lines (excluding contracts)."""

    MAX_LINES = 500
    ENTRY_POINTS = {
        "operations": ["engine.py"],
        "requirements": ["engine.py"],
        "canonical": ["engine.py"],
        "detection": ["engine.py"],
        "connection": ["manager.py"],
        "processing": ["engine.py"],
        "validation": ["engine.py"],
        "output": ["engine.py"],
        "flush": ["engine.py"],
    }

    @pytest.mark.architecture
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "layer_key", ["operations", "requirements", "canonical", "detection", "connection"]
    )
    def test_layer_has_exactly_one_entry_point(self, layer_key: str):
        layer_dir = ALL_LAYERS[layer_key]
        expected = self.ENTRY_POINTS[layer_key]
        entry_files = [layer_dir / e for e in expected]
        found = [f for f in entry_files if f.exists()]
        assert len(found) == 1, (
            f"{layer_key}/ must contain exactly one entry point {expected}, "
            f"found {len(found)}: {found}"
        )

    @pytest.mark.architecture
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "layer_key", list(ALL_LAYERS.keys())
    )
    def test_no_god_modules(self, layer_key: str):
        layer_dir = ALL_LAYERS[layer_key]
        violations: list[tuple[Path, int]] = []
        for f in _py_files(layer_dir):
            if f.name == "contracts.py":
                continue  # Contracts file is expected to be large
            try:
                line_count = sum(
                    1 for _ in f.open(encoding="utf-8")
                )
            except UnicodeDecodeError:
                continue
            if line_count > self.MAX_LINES:
                violations.append((f, line_count))
        if violations:
            msg_lines = [
                f"God modules found in {layer_key}/ "
                f"(>{self.MAX_LINES} lines):"
            ]
            for fp, count in violations:
                msg_lines.append(f"  {fp} ({count} lines)")
            pytest.fail("\n".join(msg_lines))
