# Compatibility Matrix — DVA Platform v2.0.0

## Supported Versions

| Component | Minimum | Recommended | Maximum |
|-----------|---------|-------------|---------|
| Python    | 3.12    | 3.12        | 3.13    |
| NiceGUI   | 1.4.0   | 1.4.15      | 1.5.x   |
| Polars    | 0.20.0  | 0.20.19     | 0.21.x  |
| DuckDB    | 0.9.0   | 0.10.0      | 0.10.x  |
| PyArrow   | 14.0.0  | 15.0.0      | 16.0.x  |

## Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| Linux (x86_64) | ✅ Fully Supported | Primary development platform |
| Linux (aarch64) | ✅ Supported | Limited testing |
| Windows 10/11 | ✅ Supported | File paths must use forward slashes or escaped backslashes |
| macOS (Intel) | ⚠️ Community Support | Not officially tested |
| macOS (Apple Silicon) | ⚠️ Community Support | Rosetta 2 required for some native libs |

## Dependency Pinning

All dependencies should be pinned to exact versions in production.

## Component Compatibility Details

### Python
- **Minimum**: 3.12.0 — Required for language features (type parameter syntax, improved error messages)
- **Recommended**: 3.12.x — Latest stable 3.12 release with security patches
- **Maximum**: 3.13.x — Known to work but not extensively tested
- **Not Supported**: Python 3.11 and earlier; 3.14 and later (untested)

### NiceGUI
- **Minimum**: 1.4.0 — Required for UI component APIs used by the platform
- **Recommended**: 1.4.15 — Latest stable release with bug fixes
- **Maximum**: 1.5.x — Forward-compatible; breaking changes in 2.0 not yet evaluated
- **Key Features Used**: UI elements, event system, dark mode, styling

### Polars
- **Minimum**: 0.20.0 — Required for DataFrame operations and expression API
- **Recommended**: 0.20.19 — Latest stable 0.20.x release
- **Maximum**: 0.21.x — API stability may introduce deprecation warnings but maintains compatibility
- **Key Features Used**: DataFrame, lazy API, expressions, streaming, IO

### DuckDB
- **Minimum**: 0.9.0 — Required for SQL-based temporary data operations
- **Recommended**: 0.10.0 — Latest stable release with performance improvements
- **Maximum**: 0.10.x — Minor releases are backward-compatible
- **Key Features Used**: SQL execution, in-memory database, Polars integration

### PyArrow
- **Minimum**: 14.0.0 — Required for Arrow format support and Polars integration
- **Recommended**: 15.0.0 — Latest stable release with feature improvements
- **Maximum**: 16.0.x — Known compatible version range
- **Key Features Used**: Arrow tables, Parquet, memory pools, type system

## Python Package Compatibility

| Package | Minimum | Maximum | Notes |
|---------|---------|---------|-------|
| nicegui | 1.4.0 | 1.5.x | Core UI framework |
| polars | 0.20.0 | 0.21.x | Data processing engine |
| duckdb | 0.9.0 | 0.10.x | Temporary data storage |
| pyarrow | 14.0.0 | 16.0.x | Columnar format support |
| psutil | 5.9.0 | latest | System monitoring |

## Tested Configurations

| Configuration | Python | NiceGUI | Polars | DuckDB | PyArrow | Status |
|---------------|--------|---------|--------|--------|---------|--------|
| Ubuntu 22.04 | 3.12.3 | 1.4.15 | 0.20.19 | 0.10.0 | 15.0.0 | ✅ Full |
| Ubuntu 24.04 | 3.12.7 | 1.4.17 | 0.20.22 | 0.10.2 | 15.0.2 | ✅ Full |
| Windows 11 | 3.12.5 | 1.4.15 | 0.20.19 | 0.10.0 | 15.0.0 | ✅ Full |
| macOS 14 (Intel) | 3.12.4 | 1.4.15 | 0.20.19 | 0.10.0 | 15.0.0 | ⚠️ Community |
| macOS 15 (Apple Silicon) | 3.13.0 | 1.5.0 | 0.21.0 | 0.10.2 | 16.0.0 | ⚠️ Community |
| RHEL 9 | 3.12.3 | 1.4.15 | 0.20.19 | 0.10.0 | 15.0.0 | ✅ Full |

## Third-Party Dependency Notes

### System Packages

**Linux (Debian/Ubuntu)**:
```bash
sudo apt install python3.12 python3.12-venv python3-pip build-essential
```

**Linux (RHEL/Fedora)**:
```bash
sudo dnf install python3.12 python3.12-pip python3-devel gcc
```

**Windows**:
- Python 3.12+ from python.org
- Microsoft Visual C++ Redistributable
- No additional system packages required

**macOS**:
- Python 3.12+ from python.org or Homebrew
- Xcode Command Line Tools for native package compilation

## Version Validation

Use the dependency checker script to validate your installation:

```bash
python3 scripts/dependency_checker.py
```

This script checks all required packages against the minimum and maximum versions listed in this matrix.

## Upgrading Components

When upgrading individual components, always verify:
1. All other dependencies remain within their supported ranges
2. Run the full test suite after upgrading
3. Check for deprecation warnings in logs
4. Validate end-to-end processing with representative data

## Notes

- Versions outside the supported ranges may work but are not tested or guaranteed
- Always test upgrades in a staging environment before applying to production
- Report compatibility issues with specific version combinations to the development team
- The compatibility matrix is updated with each release
