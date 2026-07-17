# Sprint 2: Detection Layer

## Responsibilities

- Detect file type (delimited, fixed-width, multiline, Excel)
- Detect delimiter, encoding, header
- Detect record types, prefixes (HDR, S, U, H, D, T)
- Detect trailer prefix
- Generate candidate column mappings
- Compute confidence scores
- Generate warnings and recommendations

Output: `DiscoveryResult` — the ONLY source of truth.

**No downstream rediscovery allowed.**

## Contract

`DiscoveryResult` defines the output:

```python
@dataclass
class DiscoveryResult:
    file_path: str
    file_type: FileType
    delimiter: Optional[str]
    encoding: str
    has_header: bool
    is_multiline: bool
    header_prefix: Optional[str]
    trailer_prefix: Optional[str]
    record_types: List[str]
    columns: List[str]
    candidate_quantity_columns: List[str]
    candidate_price_columns: List[str]
    candidate_uom_columns: List[str]
    record_hierarchy: Optional[Dict]
    confidence: float
    warnings: List[str]
    recommendations: List[str]
```

## Detection Modules

| Module | Responsibility |
|--------|---------------|
| `engine.py` | Main orchestrator — `DetectionEngine.detect()` |
| `delimiter.py` | Delimiter detection and consistency validation |
| `header.py` | Header row and HDR prefix detection |
| `multiline.py` | Multiline record and trailer prefix detection |
| `candidates.py` | Canonical column mapping heuristics |
| `confidence.py` | Confidence score calculation |

## Usage

```python
from dav_platform.connection.local import LocalDataSource
from dav_platform.detection.engine import DetectionEngine

source = LocalDataSource()
engine = DetectionEngine(source)
result = engine.detect("/path/to/file.csv")

print(result.file_type)      # FileType.DELIMITED
print(result.delimiter)       # ","
print(result.has_header)      # True
print(result.confidence)      # 0.95
```

## Supported File Types

| Type | Detection Method |
|------|-----------------|
| Delimited (CSV, pipe, tab, semicolon) | Delimiter frequency analysis |
| Fixed Width | Fallback when no delimiter found |
| Multiline | Prefix detection (H\|, D\|, T\|) |
| Fixed Width Multiline | Alphabetic prefix + digit pattern |
| Excel | File extension (.xlsx, .xls) |

## Confidence Score

Range: 0.0 — 1.0

Penalties:
- Fixed-width files: -0.3
- Ambiguous delimiter: -0.15
- No header row: -0.1
- Multiline without prefixes: -0.2
- Multiline without trailer: -0.1

## Test Coverage

55 new unit tests (94 total):
- Delimiter detection: 9 tests
- Header detection: 9 tests
- Multiline detection: 10 tests
- Candidate columns: 9 tests
- Confidence scores: 6 tests
- DetectionEngine: 7 tests
- Sprint 1 tests: 39 tests

All tests pass.
