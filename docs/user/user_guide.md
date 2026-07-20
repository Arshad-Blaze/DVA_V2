# User Guide — DVA Platform v2

## Introduction

DVA Platform v2 is a comprehensive retail data processing platform designed to ingest raw retail data files from diverse sources, automatically detect their structure, transform them into a standardized canonical format, and execute configurable processing workflows. The platform produces validated outputs suitable for business analysis, reporting, and downstream systems.

### Key Capabilities

- **Multi-source data ingestion** — Local filesystems, network shares, and remote data sources
- **Automatic file structure detection** — Delimiter, encoding, header detection, column types
- **Canonical transformation** — Maps retailer-specific column names to standardized business columns
- **Configurable processing** — Aggregation, calculation, validation, and reporting
- **Multi-format export** — Excel, CSV, and JSON output
- **Session persistence** — Projects, connections, and workspace state survive restarts

### Architecture Overview

The platform is built on a strict layered architecture:

```
Data Source → Connection → Detection → Canonical → Requirement → 
Operation → Processing → Validation → Reporting → Output
```

Each layer consumes the output of the previous layer and produces structured data for the next. No layer bypasses are permitted.

## Workspace Reference

### Home Workspace

The landing page after completing the Welcome Wizard. Provides:
- Recent projects quick-access
- System status indicators
- Navigation to all workspaces
- Global search bar

### Projects Workspace

Manage your data processing projects:
- **Create Project** — Name, description, and metadata
- **Open Project** — Load previously saved project state
- **Clone Project** — Duplicate an existing project with all settings
- **Delete Project** — Remove project and its associated data
- **Project Properties** — View and edit metadata, creation date, last modified

Each project maintains its own set of connections, detection results, mappings, and processing configurations.

### Connection Workspace

Configure and manage data sources:

#### Supported Source Types
- **Local Folder** — Direct filesystem access (full read/write)
- **Network Share** — SMB/CIFS mounts (read-only by default)
- **SFTP/SSH** — Remote file servers (requires credentials)
- **S3 Compatible** — Object storage (requires endpoint and credentials)

#### Operations
- **Browse** — Navigate directory tree with file preview
- **Connect** — Establish and test connection
- **Disconnect** — Release connection resources
- **File Preview** — View first N rows of a data file
- **Directory Summary** — File counts, sizes, and extension distribution

#### Adaptive Access Strategy

The platform automatically selects the optimal data access method based on directory size:
- **Small datasets** (< 100MB): Direct in-memory loading
- **Medium datasets** (100MB–1GB): Stream-based processing
- **Large datasets** (> 1GB): Chunked streaming with progress reporting

### Detection Workspace

Automatically analyzes file structure and characteristics:

#### Detection Results

| Property | Description |
|----------|-------------|
| **File Type** | Delimited, fixed-width, Excel, multiline, mixed-record |
| **Delimiter** | Auto-detected (comma, tab, pipe, semicolon, custom) |
| **Encoding** | UTF-8, UTF-16, Latin-1, ANSI |
| **Header Detection** | Presence and confidence of header row |
| **Column Detection** | Names and count of data columns |
| **Record Types** | For multiline files, distinct record formats |
| **Field Layout** | For fixed-width files, start positions and widths |

#### Column Role Detection

The Detection workspace identifies candidate columns for 19 business roles:
- Store, UPC, Description, Brand, Department, Category
- Units, Weighted Quantity, Price, Sales, Currency
- Date, Time, Promotion, Store Type, Region, Division, UoM, Record Type

#### Quantity Intelligence

Automatically recommends the best quantity column based on data analysis, distinguishing between weighted quantity and unit count.

### Canonical Workspace

Transforms physical column names to standardized canonical names:

#### Standard Canonical Columns

| Canonical Name | Description |
|----------------|-------------|
| `store` | Store identifier |
| `upc` | Universal Product Code |
| `description` | Product description |
| `quantity` | Resolved quantity (weighted or units) |
| `weight` | Weight value |
| `price` | Unit price |
| `category` | Product category |
| `brand` | Product brand |
| `department` | Department identifier |
| `date` | Transaction date |
| `uom` | Unit of measure |

#### Mapping Sources
- **Candidate** — Auto-detected column role mappings (confidence-scored)
- **Rule** — User-defined mapping rules applied automatically
- **User** — Manual overrides
- **Default** — Fallback when no mapping is found

#### Transformation Strategies
- **Direct** — Simple rename (standard delimited files)
- **Multiline** — Flatten multi-record files to single rows
- **Hierarchy** — Resolve parent-child record structures

### Preview Workspace

Inspect data before processing:
- **Raw Preview** — Original file contents
- **Flatten Preview** — After multiline/hierarchy flattening
- **Canonical Preview** — After column mapping
- **Row Count** — Total data rows
- **Column Summary** — Each column's type, null count, unique values

### Requirements Workspace

Define processing requirements:

#### Business Goals
- **Raw Review** — Inspect data without transformation
- **Validation** — Run validation rules against data
- **Format Change** — Convert between file formats
- **Migration** — Prepare data for system migration
- **Comparison** — Compare datasets (requires two sources)
- **Reporting** — Generate summary reports
- **Aggregation** — Group and summarize data
- **Calculation** — Apply formulas and derived columns

#### Capability Matrix

The platform evaluates your data and shows which business goals are supported. Unsupported operations are grayed out with explanations.

#### Execution Plan

Generated automatically based on your selected business goals. Shows each step, the layer responsible, and dependencies.

### Operation Workspace

Execute processing workflows:
- **Execution Plan** — Visual step-by-step plan
- **Run** — Execute all steps sequentially
- **Step-by-Step** — Execute one step at a time with review
- **Cancel** — Stop a running execution
- **Retry** — Re-run failed steps

#### Execution States

| State | Description |
|-------|-------------|
| PENDING | Waiting to execute |
| RUNNING | Currently executing |
| COMPLETED | Executed successfully |
| FAILED | Execution encountered error |
| SKIPPED | Skipped due to dependency failure |
| CANCELLED | User cancelled execution |

### Processing Workspace

Configure and run data transformations:

#### Aggregation
- **Group By** — Select one or more grouping columns (store, UPC, category, etc.)
- **Aggregations** — Sum, Mean, Count, Min, Max, First, Last
- **Multiple Aggregations** — Apply different strategies to different columns

#### Calculations
- **Derived Columns** — Create new columns based on expressions
- **Operations** — Sum, difference, ratio, average, min, max
- **Custom Expressions** — Polars expression language

#### Statistics
- Row counts and unique value counts per column
- Null percentage detection
- Distribution analysis
- Duplicate detection

### Validation Workspace

Validate data quality and consistency:

#### Validation Categories
- **Completeness** — Missing value checks per column
- **Consistency** — Cross-column relationship checks
- **Uniqueness** — Duplicate detection in key columns
- **Null Checks** — Null percentage thresholds
- **Range Checks** — Numeric value bounds

#### Severity Levels
- **Info** — Informational observations
- **Warning** — Potential issues requiring review
- **Error** — Data quality violations
- **Critical** — Data integrity breaches

#### Validation Outputs
- Per-rule pass/fail status
- Row-level issue detail
- Aggregate statistics
- Entity-level summaries (store, UPC, category)

### Reports Workspace

Generate and export reports:

#### Report Types
- **Validation Report** — Full validation results
- **Store Summary** — Per-store aggregated metrics
- **UPC Summary** — Per-product aggregated metrics
- **Category Summary** — Category-level aggregations
- **Brand Summary** — Brand-level aggregations
- **Department Summary** — Department-level aggregations
- **Business KPIs** — Key performance indicators
- **Processing Summary** — Execution metadata

#### Export Formats
- **Excel (.xlsx)** — Multi-sheet workbook with formatted tables
- **CSV (.csv)** — Comma-separated values
- **JSON (.json)** — Structured data interchange format

#### Dashboard
A visual summary dashboard is included in Excel exports, showing:
- Pass/fail rates for validation
- Top/bottom performing stores
- Distribution charts
- Execution metrics

### Administration Workspace

System administration functions:
- **User Management** — Add/remove users (multi-user mode)
- **System Logs** — View and filter log entries
- **Cache Management** — Clear cached data
- **Maintenance** — Run maintenance tasks
- **Backup/Restore** — Create and restore system backups

### Settings Workspace

User preferences:
- **Theme** — Light, dark, high-contrast, system
- **Language** — Interface language (if translations available)
- **Notifications** — Configure notification preferences
- **Defaults** — Default export format, workspace on startup
- **Advanced** — Performance settings, cache limits

### Help Workspace

Built-in documentation:
- **Quick Start** — Getting started guide
- **User Guide** — This document (link)
- **Keyboard Shortcuts** — Available shortcuts
- **About** — Version and system information

### Developer Workspace

Tools for developers and power users:
- **API Console** — Test backend services directly
- **Log Viewer** — Real-time log stream
- **Component Browser** — View registered workspace components
- **Performance Metrics** — Execution timing and memory usage

### Health Workspace

System health monitoring:
- **Service Status** — All backend services status
- **Memory Usage** — Current and peak memory
- **Uptime** — System uptime
- **Connection Pool** — Active database connections
- **Task Queue** — Pending and running tasks

## Session Management

The platform automatically saves your session state:
- Active project and connection
- Detection and canonical settings
- Workspace positions and selections
- Theme preference

Session data is stored in `~/.dva/` directory and persists across application restarts.

## Data Flow Example

### End-to-End Workflow

1. **Create Project** → "Q4 Sales Analysis"
2. **Add Connection** → Local folder `/data/retail/sales/`
3. **Browse Files** → Select `Q4_2024_sales.dat`
4. **Detect** → Tab-delimited, UTF-8, header present, 19 columns
5. **Review Detection** → Confirm column roles (Store, UPC, Sales, etc.)
6. **Apply Canonical** → Map to standard names, accept quantity recommendations
7. **Preview** → Verify 50,000 rows with 11 canonical columns
8. **Set Requirements** → Goal: "Aggregation", Group by: store, Aggregate: sum(sales)
9. **Execute** → Run workflow, monitor progress
10. **Validate** → Check completeness and range checks passed
11. **Report** → Export Excel with store summary and dashboard
12. **Cleanup** → Close connection, clear temp files
