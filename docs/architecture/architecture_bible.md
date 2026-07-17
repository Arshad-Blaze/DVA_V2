# DVA Platform v2 - Architecture Bible

## Mission

Build a Retail Data Processing Platform that is:
- Simple
- Clean
- Modular
- Streaming First
- Architecture Driven
- Business Driven
- Easy to Extend, Test, Maintain

## Project Philosophy

DVA is NOT a parser.
DVA is NOT a validation tool.
DVA is a Retail Data Processing Platform.

Validation is only ONE business operation.

## Architecture Layers

```
Data Access → Detection → Canonical → Requirement → Operation → Processing → Validation → Reporting → Cleanup
```

### Layer Rules

1. Every layer owns ONE responsibility
2. Every layer owns ONE contract
3. Every layer consumes ONLY the contract produced by the previous layer
4. No layer bypasses
5. No duplicate logic

## Layer Contracts

### Sprint 1: Data Access Layer (COMPLETE)

**Contract:** `IDataSource`

**Responsibilities:**
- Connect / Disconnect
- Browse directories
- Read files (sample, stream, download)
- Get file metadata

**Data Types:**
- `DataSourceEntry`
- `DirectorySummary`
- `DataSourceError`

**Implementations:**
- `LocalDataSource`
- `SSHDataSource`

### Sprint 2/2.5: Detection Layer (COMPLETE)

**Contract:** `DiscoveryResult`

**Responsibilities:**
- Detect file type (delimited, fixed-width, multiline, Excel, mixed record)
- Detect delimiter, encoding (UTF-8, UTF-16, Latin-1)
- Detect header rows, data start, trailer start
- Detect record types dynamically (not hardcoded)
- Detect trailer prefix
- Build record hierarchy
- Generate layout intelligence for fixed-width files
- Generate candidate column mappings (19 business roles)
- Generate previews (raw, flatten, canonical)
- Compute confidence scores for every decision
- Collect comprehensive statistics
- Generate discovery reports
- Recommend quantity columns (quantity intelligence)

**Data Types:**
- `DiscoveryResult` — output contract
- `RecordTypeInfo` — detected record type with statistics
- `LayoutField` — fixed-width field suggestion
- `ExcelSheetInfo` — Excel sheet metadata
- `DetectionStatistics` — file statistics
- `CandidateMapping` — column mapping with confidence
- `QuantityRecommendation` — quantity column recommendation
- `DiscoveryContext` — internal only (never returned)

**Modules:**
- `engine.py` — DetectionEngine orchestrator
- `delimiter.py` — delimiter detection
- `header.py` — header detection
- `multiline.py` — multiline/record type detection
- `candidates.py` — 19-role column mapping
- `confidence.py` — confidence scoring
- `encoding.py` — encoding detection
- `layout.py` — fixed-width layout intelligence
- `statistics.py` — statistics collection
- `quantity.py` — quantity intelligence
- `excel.py` — Excel discovery
- `previews.py` — preview generation
- `report.py` — discovery report generation
- `context.py` — internal DiscoveryContext

**Rule:** Detection is the ONLY source of truth. No downstream rediscovery allowed.

**Test Coverage:** 102 tests (Sprint 2 + 2.5)

### Sprint 3: Canonical Layer (PENDING)

**Contract:** `CanonicalDataset`

**Responsibilities:**
- Convert Physical Schema → Business Schema → Canonical Schema
- Map retailer columns to standard names
- Resolve quantities

**Standard Columns:**
- store, upc, description, quantity, weight, price
- category, brand, department, date, uom

### Sprint 4: Requirement Layer (PENDING)

**Contract:** `OperationContext`

**Responsibilities:**
- User selects processing mode
- Aggregate Only / Aggregate + Calculate / Raw Review

### Sprint 5: Operation Layer (PENDING)

**Contract:** Operation Registry

**Responsibilities:**
- Plugin architecture
- Each operation is independent
- Operations: Aggregate, Validation, Migration, Format Change, Statistics, Export

### Sprint 6: Processing Layer (PENDING)

**Contract:** `ProcessingResult`

**Responsibilities:**
- Consumes ONLY Canonical Dataset + Operation Context
- No parsing, no delimiter knowledge, no physical schema

### Sprint 7: Validation Layer (PENDING)

**Contract:** `ValidationResult`

**Responsibilities:**
- Pure business validation
- Never aggregates, never parses

### Sprint 8: Reporting Layer (PENDING)

**Contract:** `ReportOutput`

**Responsibilities:**
- Produce Excel, CSV, Parquet
- Summary sheets (Store, Item, Category, Brand, Validation, Performance)
- Reports derive from final outputs, never re-read data

### Sprint 9: Cleanup Layer (PENDING)

**Responsibilities:**
- Always execute
- Release connections, streams, DataFrames, temp files, session, caches, memory

## Engineering Rules

- Architecture drives code
- Code never drives architecture
- Streaming First
- Polars First
- Composition over inheritance
- Small modules, small functions
- Strong typing
- High cohesion, low coupling

## Testing Strategy

Every sprint:
- Unit Tests
- Integration Tests
- Regression Tests
- Sample Datasets
- Large File Tests
- Streaming Tests

Only after tests pass, proceed to next sprint.

## UI Philosophy

UI is LAST.
UI should only:
- Collect Inputs
- Show Progress
- Render Outputs

No business logic. No parsing. No validation. No report generation.
