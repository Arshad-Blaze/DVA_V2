# Developer Guide — DVA Platform v2

## Introduction

This guide provides comprehensive information for developers working on or extending the DVA Platform v2. It covers codebase structure, development workflow, adding new features, testing, and contribution guidelines.

## Codebase Structure

```
dav_platform/           # Backend data processing engine
  core/                 # Contracts and shared types
    contracts.py        # Layer boundary contracts (dataclasses, ABCs)
  connection/           # Data Access Layer
  detection/            # Detection Layer
  canonical/            # Canonical Transformation Layer
  requirements/         # Requirements Layer
  operations/           # Operations Layer
  processing/           # Processing Layer
  validation/           # Validation Layer
  reporting/            # Reporting Layer
  output/               # Output/Export Layer
  cleanup/              # Flush/Cleanup Layer
  workflow/             # Workflow orchestration
  shared/               # Shared utilities
  ui/                   # UI integration adapters

ui/                     # Frontend (NiceGUI)
  app.py                # Application entry point
  shared.py             # Shared service instances
  shell/                # Application shell (layout, sidebar, header)
    layout.py           # Main layout composition
    sidebar.py          # Sidebar navigation
    header.py           # Top bar
    statusbar.py        # Bottom status bar
    workspace_manager.py # Workspace switching logic
  controllers/          # Controller layer
    workspace_controller.py
    session_controller.py
    navigation_controller.py
    project_controller.py
    connection_controller.py
    detection_controller.py
    canonical_controller.py
    preview_controller.py
    requirement_controller.py
    operation_controller.py
    processing_controller.py
    validation_controller.py
    reports_controller.py
    admin_controller.py
  services/             # Service layer
    # One service per domain area
    session_service.py
    project_service.py
    connection_service.py
    detection_service.py
    canonical_service.py
    preview_service.py
    requirement_service.py
    operation_service.py
    processing_service.py
    validation_service.py
    reports_service.py
    admin_service.py
    navigation_service.py
    notification_service.py
    theme_service.py
    persistence_service.py
    storage_service.py
    migration_service.py
    welcome_service.py
    demo_service.py
    guidance_service.py
    serialization_service.py
    workspace_context.py
  workspaces/           # UI workspace renderers
    home/               # Home workspace
    projects/           # Projects workspace
    connection/         # Connection workspace
    detection/          # Detection workspace
    canonical/          # Canonical workspace
    preview/            # Preview workspace
    requirement/        # Requirements workspace
    operation/          # Operation workspace
    processing/         # Processing workspace
    validation/         # Validation workspace
    reports/            # Reports workspace
    administration/     # Administration workspace
    settings/           # Settings workspace
    help/               # Help workspace
    developer/          # Developer tools workspace
    health/             # Health monitoring workspace
    welcome/            # First-run wizard
  styles/               # Custom CSS styles
  themes/               # Theme definitions (dark, light, high_contrast)
  assets/               # Static assets (images, fonts)

tests/                  # Test suite
  unit/                 # Unit tests
  integration/          # Integration tests
  fixtures/             # Test data fixtures

scripts/                # Utility scripts
  dependency_checker.py
  environment_validation.py
  startup_validation.py
```

## Architecture Principles

### Layer Architecture

The platform enforces a strict layered architecture where each layer produces a contract consumed by the next:

```
Connection → Detection → Canonical → Requirement → Operation → Processing → Validation → Reporting → Output → Cleanup
```

### Engineering Rules

1. **Architecture drives code** — All code must conform to the defined layer architecture
2. **No layer bypasses** — A layer cannot skip to another layer's output
3. **Streaming First** — Process data in streams where possible
4. **Polars First** — Use Polars DataFrames as the primary data structure
5. **Composition over inheritance** — Prefer composition for code reuse
6. **Small modules, small functions** — Keep files under 500 lines, functions under 50 lines
7. **Strong typing** — All function signatures must have type annotations
8. **High cohesion, low coupling** — Related code stays together; layers communicate only through contracts

## Contracts

Every layer defines its contract in `dav_platform/core/contracts.py`. Contracts are:
- **Dataclasses** for data structures
- **Abstract base classes** for service interfaces
- **Enums** for fixed sets of values

### Current Contracts

| Layer | Contract Type | Key Classes |
|-------|--------------|-------------|
| Connection | ABC | `IDataSource`, `DataSourceEntry`, `DirectorySummary` |
| Detection | Dataclass | `DiscoveryResult`, `DetectionStatistics`, `FileType` |
| Canonical | Dataclass | `CanonicalDataset`, `CanonicalMetadata`, `ColumnMapping` |
| Requirement | Dataclass | `OperationContext`, `CapabilityMatrix`, `BusinessGoal` |
| Operation | Dataclass | `ExecutionResult`, `ExecutionStepResult` |
| Processing | Dataclass | `ProcessingResult`, `ProcessingConfig`, `AggregationConfig` |
| Validation | Dataclass | `ValidationResult`, `ValidationConfig`, `ValidationIssue` |
| Reporting | Dataclass | `ValidationReportData`, `OutputConfig` |
| Output | Dataclass | `OutputArtifacts`, `ExportManifest` |
| Cleanup | Dataclass | `FlushResult`, `CleanupSummary`, `ExecutionMetrics` |

## Adding a New Feature

### Step 1: Define the Contract

Add your dataclasses and interfaces to `dav_platform/core/contracts.py`. Ensure backward compatibility with existing contracts.

```python
@dataclass
class MyNewResult:
    field1: str = ""
    field2: int = 0
```

### Step 2: Implement the Backend Layer

Create a new module under `dav_platform/<layer>/`:

```python
# dav_platform/my_layer/processor.py
from dav_platform.core.contracts import MyNewResult

class MyProcessor:
    def process(self, input_data) -> MyNewResult:
        ...
```

### Step 3: Create a Service

Create a service in `ui/services/`:

```python
# ui/services/my_service.py
from dav_platform.my_layer.processor import MyProcessor
from ui.services.workspace_context import WorkspaceContext

class MyService:
    def __init__(self, context: WorkspaceContext):
        self.processor = MyProcessor()
        self.context = context
    
    def do_something(self) -> dict:
        result = self.processor.process(...)
        return {"status": "ok", "result": result}
```

### Step 4: Create a Controller

Create a controller in `ui/controllers/`:

```python
# ui/controllers/my_controller.py
from ui.services.my_service import MyService
from ui.services.notification_service import NotificationService

class MyController:
    def __init__(self, service: MyService, notify: NotificationService):
        self.service = service
        self.notify = notify
    
    def handle_action(self) -> None:
        result = self.service.do_something()
        self.notify.info("Action completed")
```

### Step 5: Create a Workspace

Create a workspace renderer in `ui/workspaces/`:

```python
# ui/workspaces/my_feature/workspace.py
from nicegui import ui
from ui import shared

def render():
    ctrl = shared.my_ctrl()
    
    with ui.column():
        ui.label("My Feature").classes("text-h4")
        
        def on_click():
            ctrl.handle_action()
        
        ui.button("Do Something", on_click=on_click)
```

### Step 6: Register the Workspace

In `ui/app.py`:

```python
from ui.workspaces.my_feature.workspace import render as render_my_feature

# In main():
ws_ctrl.register("my_feature", render_my_feature)
```

### Step 7: Add to Shared

In `ui/shared.py`:

```python
from ui.services.my_service import MyService
from ui.controllers.my_controller import MyController

# Add lazy-initialized singleton
_my_svc: Optional[MyService] = None
_my_ctrl: Optional[MyController] = None

# In init_all():
_my_svc = MyService(_context)
_my_ctrl = MyController(_my_svc, _notify_svc)

# Add accessor functions
def my_svc() -> MyService: ...
def my_ctrl() -> MyController: ...
```

## Service-Controller Pattern

The UI follows a strict service-controller pattern:

- **Services** contain business logic and state management. They are pure Python with no UI imports.
- **Controllers** handle user actions, call services, manage notifications. They bridge UI events to services.
- **Workspace renderers** define UI layout using NiceGUI components. They call controllers, never services directly.

```
User Action → Workspace Renderer → Controller → Service → Backend Layer
```

## Testing

### Test Framework

The project uses pytest for testing. Configuration is in `pytest.ini`.

### Running Tests

```bash
# Run all tests
python3 -m pytest

# Run unit tests only
python3 -m pytest tests/unit/ -v

# Run specific test file
python3 -m pytest tests/unit/test_detection.py -v

# Run with coverage
python3 -m pytest --cov=dav_platform tests/ -v
```

### Writing Tests

```python
# tests/unit/test_my_feature.py
import pytest
from dav_platform.my_layer.processor import MyProcessor

class TestMyProcessor:
    def test_process_basic(self):
        proc = MyProcessor()
        result = proc.process(...)
        assert result.field1 == expected_value
```

### Test Structure

- **Unit tests** test individual classes and functions in isolation
- **Integration tests** test layer interactions through contracts
- **Test fixtures** are stored in `tests/fixtures/`

## Development Workflow

### 1. Setup Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 2. Run the Application

```bash
python3 -m ui.app
```

### 3. Make Changes

- Follow the engineering rules
- Add tests for new functionality
- Update contracts if layer boundaries change

### 4. Verify

```bash
# Run tests
python3 -m pytest

# Check dependencies
python3 scripts/dependency_checker.py

# Validate environment
python3 scripts/environment_validation.py
```

## Code Style

### Naming Conventions
- **Classes**: PascalCase
- **Functions/methods**: snake_case
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private members**: _leading_underscore

### Imports
```python
# Standard library
import sys
from pathlib import Path

# Third-party
import polars as pl
from nicegui import ui

# Local
from dav_platform.core.contracts import DiscoveryResult
from ui.services.detection_service import DetectionService
```

### Type Annotations
All function signatures must include type annotations:

```python
def process_file(path: str, chunk_size: int = 10000) -> ProcessingResult:
    ...
```

## Debugging

### Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing file: %s", path)
logger.warning("Detected potential issue: %s", issue)
logger.error("Failed to process: %s", error)
```

### Developer Workspace

The Developer workspace provides:
- **API Console** — Test service calls directly
- **Log Stream** — Real-time log viewer
- **Component Browser** — Inspect registered components
- **Performance Metrics** — Execution timing data

## Performance Considerations

- Use Polars over Pandas for DataFrame operations
- Enable streaming for files over 100MB
- Avoid loading entire datasets into memory
- Use chunked processing for large files
- Profile before optimizing — avoid premature optimization
- The streaming flag (`ProcessingConfig.streaming`) enables chunk-based processing

## Contribution Guidelines

1. **Branch naming**: `feature/<name>`, `fix/<name>`, `docs/<name>`
2. **Commit messages**: Concise, descriptive, referencing issues
3. **Pull requests**: Include test coverage and documentation updates
4. **Code review**: All changes require review by at least one maintainer
5. **Backward compatibility**: Don't break existing contracts without migration path
6. **Documentation**: Update relevant docs when changing behavior

## Getting Help

- Internal documentation: `docs/` directory
- Architecture decisions: `docs/architecture/`
- Sprint reports: `docs/developer/`
- Ask in team channels
- File issues in the project repository
