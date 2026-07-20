# Architecture Guide — DVA Platform v2

## Overview

DVA Platform v2 is built on a strict layered architecture that enforces separation of concerns and guarantees data flow integrity. Each layer has a single responsibility, a well-defined contract, and communicates only with adjacent layers through these contracts.

## Architectural Philosophy

```
"Architecture drives code. No layer bypasses. Streaming First. Polars First."
```

The platform follows these core principles:

1. **Strict Layering** — Each layer produces one contract consumed by the next layer
2. **Contract-Driven Design** — Layer boundaries are defined by immutable dataclass contracts
3. **Unidirectional Data Flow** — Data flows forward through the pipeline without skipping layers
4. **Streaming Capability** — Data is processed in streams where possible, avoiding full materialization
5. **Polars Native** — All data manipulation uses Polars DataFrames

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                         │
│   (NiceGUI Web UI — Workspaces, Shell, Services)          │
├─────────────────────────────────────────────────────────┤
│                    Controller Layer                        │
│   (Bridges UI events to service calls)                    │
├─────────────────────────────────────────────────────────┤
│                    Service Layer                           │
│   (Business logic, state management)                      │
├─────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│ │Connection│→│Detection │→│Canonical │→│  Requirement  │ │
│ │  Layer   │ │  Layer   │ │  Layer   │ │    Layer      │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
│        ↓                                                  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│ │Operation │→│Processing│→│Validation│→│  Reporting    │ │
│ │  Layer   │ │  Layer   │ │  Layer   │ │    Layer      │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────────┘ │
│        ↓                                                  │
│ ┌──────────┐ ┌──────────┐                                 │
│ │  Output  │→│  Flush   │                                 │
│ │  Layer   │ │  Layer   │                                 │
│ └──────────┘ └──────────┘                                 │
└─────────────────────────────────────────────────────────┘
```

## Layer Contracts

Each layer defines its input and output contracts in `dav_platform/core/contracts.py`. Contracts serve as the sole interface between layers.

### Connection Layer Contract

**Input**: User-specified connection parameters (path, URL, credentials)
**Output**: `IDataSource` — Abstract interface for browsing, reading, and streaming files

**Responsibility**: Abstract access to diverse data sources (local filesystem, network shares, remote servers). Provides file listing, reading, streaming, and metadata queries without exposing source-specific details.

**Key Interfaces**:
- `IDataSource.connect() / disconnect()`
- `IDataSource.list_directory()`
- `IDataSource.read_sample()`
- `IDataSource.open_stream()`
- `IDataSource.directory_summary()`

### Detection Layer Contract

**Input**: File path and raw file content via `IDataSource`
**Output**: `DiscoveryResult` — Comprehensive file structure metadata

**Responsibility**: Analyze a raw data file to determine its physical structure — file type, delimiter, encoding, column layout, header position, record types. Also performs column role detection (identifying which columns map to business roles like Store, UPC, Sales) and quantity intelligence.

**Key Output Fields**:
- `file_type`, `delimiter`, `encoding`
- `has_header`, `columns`, `record_types`
- `candidate_store`, `candidate_upc`, ... (19 candidate role lists)
- `quantity_recommendation`
- `statistics`, `confidence`, `warnings`

### Canonical Layer Contract

**Input**: `DiscoveryResult` (output of Detection)
**Output**: `CanonicalDataset` — Standardized dataset with business-meaningful column names

**Responsibility**: Transform physical (retailer-specific) column names into standardized canonical column names. Applies automatic mapping from detected candidate roles, user-defined rules, and manual overrides. Handles flattening of multiline files and hierarchical records.

**Key Canonical Columns**:
`store`, `upc`, `description`, `quantity`, `weight`, `price`, `category`, `brand`, `department`, `date`, `uom`

### Requirement Layer Contract

**Input**: `CanonicalDataset` (output of Canonical)
**Output**: `OperationContext` — Processing requirements and execution plan

**Responsibility**: Determine what operations the data supports (via CapabilityMatrix), capture user's business goals, and generate an execution plan. Bridges the gap between data understanding and processing execution.

**Key Output Fields**:
- `business_goal` — User's objective
- `capability_matrix` — What operations are feasible
- `execution_plan` — Ordered list of steps
- `recommended_workflow` — Suggested workflow name

### Operation Layer Contract

**Input**: `OperationContext` (output of Requirement)
**Output**: `ExecutionResult` — Step-by-step execution results

**Responsibility**: Orchestrate execution of the processing plan. Manages step sequencing, state tracking, error handling, retries, and cancellation. Delegates actual computation to the Processing layer.

**Key Output Fields**:
- `state` — Overall execution state
- `step_results` — Per-step execution outcomes
- `metadata` — Execution timing and statistics
- `warnings`, `errors`

### Processing Layer Contract

**Input**: Execution steps from Operation layer, canonical data
**Output**: `ProcessingResult` — Processed DataFrame

**Responsibility**: Perform data transformations including aggregation (group by with sum/mean/count/min/max), calculations (derived columns, ratios, differences), and statistics computation. Uses Polars for all DataFrame operations.

**Key Configuration**:
- `group_columns`, `aggregation_configs`
- `calculation_configs`, `chunk_size`
- `streaming`, `compute_statistics`

### Validation Layer Contract

**Input**: Processed DataFrame, validation rules
**Output**: `ValidationResult` — Validation outcomes

**Responsibility**: Evaluate data quality against configurable rules. Checks completeness, consistency, uniqueness, null thresholds, and value ranges. Produces per-entity (store, UPC, category) summaries.

**Key Output Fields**:
- `passed` — Overall pass/fail
- `issues` — Individual validation issues with severity
- `total_rows_checked`, `error_count`, `warning_count`

### Reporting Layer Contract

**Input**: Validation results, processing results, output config
**Output**: `ValidationReportData`, `OutputArtifacts` — Structured report data and generated files

**Responsibility**: Compile validation and processing results into structured reports. Generates multi-sheet Excel workbooks, CSV files, and JSON exports with summaries, dashboards, and metadata.

**Key Output Formats**:
- Excel (.xlsx) with formatted sheets and dashboard
- CSV (.csv) with headers
- JSON (.json) structured export

### Output Layer Contract

**Input**: Report data and export configuration
**Output**: `OutputArtifacts` — Generated output files

**Responsibility**: Generate output files in requested formats. Manages file naming, directory structure, formatting, and metadata. Produces export manifests.

**Key Output Fields**:
- `excel_files`, `csv_files`, `json_files`
- `manifest` — Export manifest
- `statistics` — Generation statistics

### Flush Layer Contract

**Input**: Execution metadata and cleanup configuration
**Output**: `FlushResult` — Cleanup summary and lifecycle metrics

**Responsibility**: Clean up resources after workflow completion. Deletes temporary files, closes connections, clears caches, and generates lifecycle summaries.

**Key Output Fields**:
- `cleanup` — Files deleted, connections closed
- `metrics` — Total execution time, layer timings, peak memory
- `summary` — Lifecycle summary with status

## UI Architecture

The frontend follows a three-layer architecture:

### 1. Shell Layer (`ui/shell/`)
The application shell provides the persistent UI chrome:
- **Layout** — Main page structure with sidebar, header, content area, status bar
- **Sidebar** — Navigation menu with workspace switching
- **Header** — Session controls, theme toggle, notifications
- **StatusBar** — Connection status, active project, processing indicator
- **WorkspaceManager** — Handles workspace registration and switching

### 2. Service Layer (`ui/services/`)
Services contain business logic and state. They are:
- Instantiated once as singletons via `ui/shared.py`
- Context-aware via `WorkspaceContext`
- UI-agnostic (no NiceGUI imports)
- Responsible for state persistence and restoration

### 3. Controller Layer (`ui/controllers/`)
Controllers bridge UI events to service calls:
- Handle user actions from workspace renderers
- Call service methods for business logic
- Manage notifications and user feedback
- Coordinate between multiple services

### 4. Workspace Renderers (`ui/workspaces/`)
Workspace renderers define the UI for each workspace:
- Pure UI code using NiceGUI components
- Call controllers for actions
- Access services for data display
- Follow a consistent pattern: `render()` function registered with WorkspaceController

## Data Flow

### End-to-End Data Flow

```
User selects file
  → Connection Layer: Browse and select source file
    → Detection Layer: Analyze structure → DiscoveryResult
      → Canonical Layer: Map to standard columns → CanonicalDataset
        → Requirement Layer: Set business goal → OperationContext
          → Operation Layer: Execute plan → ExecutionResult
            → Processing Layer: Transform data → ProcessingResult
              → Validation Layer: Check quality → ValidationResult
                → Reporting Layer: Compile reports → OutputArtifacts
                  → Output Layer: Export files
                    → Flush Layer: Cleanup resources
```

### Navigation Flow (UI)

```
User clicks sidebar item
  → NavigationController.navigate(workspace_id)
    → NavigationService updates current workspace
      → SessionService saves current_workspace
        → WorkspaceManager.switch_to(workspace_id)
          → Active workspace render function called
            → Renders workspace content via NiceGUI
```

### Session Persistence Flow

```
Application starts
  → StorageService loads from ~/.dva/
    → MigrationService runs pending migrations
      → PersistenceService.restore_session()
        → WorkspaceContext populated with saved state
          → Theme applied, project restored, connection restored

User makes changes
  → Auto-save triggered (on navigation, or periodic)
    → PersistenceService.save_session()
      → StorageService writes to ~/.dva/
```

## Contract Design Principles

1. **Single Source of Truth** — `DiscoveryResult` is the only source of file structure information. No downstream layer may re-detect.
2. **Immutable Contracts** — Contracts are dataclasses that should be treated as immutable after creation.
3. **Explicit State** — All layer state is captured in the contract; no hidden state.
4. **Forward Compatibility** — New fields in contracts should have defaults for backward compatibility.
5. **Confidence Scoring** — Auto-detected values include confidence scores for user decision-making.

## Plugin Architecture

DVA Platform supports extension through plugins. See the [Plugin Guide](../developer/plugin_guide.md) for details.

Key extension points:
- **Connection Plugins** — New data source types (IDataSource implementations)
- **Detection Plugins** — Custom file type detection or column role detection
- **Processing Plugins** — Custom aggregation strategies or calculations
- **Validation Plugins** — Custom validation rules
- **Export Plugins** — New output formats
- **Theme Plugins** — Custom UI themes

## Performance Architecture

### Streaming Pipeline

Data flows through the pipeline in streams to minimize memory usage:

```
Small files (< 100MB): Full DataFrame in memory
Medium files (100MB-1GB): Stream-based processing
Large files (> 1GB): Chunked streaming with progress
```

### Chunked Processing

The Processing layer supports chunk-based processing:
- Configurable chunk size (default: 10,000 rows)
- Progress reporting per chunk
- Memory-efficient aggregation across chunks
- Automatic fallback to non-streaming for small datasets

### Memory Management

- Temporary files stored in system temp directory
- Cache size configurable via settings
- Automatic cache eviction based on LRU
- Explicit cache clearing in Administration workspace
- Flush layer ensures complete resource cleanup

## Security Architecture

- **Data isolation** — Each project's data is isolated
- **Path validation** — All file paths validated to prevent traversal
- **No remote connections** — No outbound network connections from the platform
- **Local storage** — All session and configuration data stored locally
- **File sanitization** — Imported file names sanitized
