# Plugin Guide — DVA Platform v2

## Introduction

DVA Platform v2 supports extension through plugins at multiple integration points. Plugins allow developers to add custom functionality without modifying the core codebase. This guide explains the plugin system architecture, available extension points, and how to create and integrate plugins.

## Plugin Architecture

The plugin system is built on a registration-based architecture:

```
Plugin Module → Plugin Registry → Extension Point → Platform Integration
```

Each plugin registers itself for specific extension points. The platform discovers and loads plugins at startup, making their capabilities available throughout the application.

### Extension Points

| Extension Point | Interface | Description |
|----------------|-----------|-------------|
| Data Sources | `IDataSource` | New types of data source connectors |
| File Detection | Custom | Custom file format detection algorithms |
| Column Role Detection | Custom | New column role identification strategies |
| Canonical Mappings | `ColumnMapping` | Custom mapping rules |
| Aggregation Strategies | `AggregationStrategy` | Custom aggregation functions |
| Calculations | `CalculationConfig` | Custom calculation operations |
| Validation Rules | `ValidationRule` | Custom validation rule types |
| Output Formats | Custom | New export formats |
| UI Themes | Custom | Custom UI themes |
| UI Widgets | Custom | Custom UI workspace components |

## Creating a Connection Plugin

Connection plugins implement the `IDataSource` interface to support new data source types.

### Step 1: Implement IDataSource

```python
# my_plugin/data_source.py
from dav_platform.core.contracts import IDataSource, DataSourceEntry, DirectorySummary

class MyCloudDataSource(IDataSource):
    """Custom cloud storage data source."""
    
    def __init__(self, config: dict):
        self.config = config
        self._connected = False
        self._client = None
    
    def connect(self) -> bool:
        # Establish connection to cloud service
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        self._client = None
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    @property
    def supports_direct_path(self) -> bool:
        return False
    
    def list_directory(self, path: str) -> list[DataSourceEntry]:
        # List files in cloud bucket/directory
        ...
    
    def list_files(self, path: str) -> list[str]:
        ...
    
    def read_sample(self, path: str, n: int = 100) -> str:
        ...
    
    def open_stream(self, path: str):
        ...
    
    def download_if_required(self, path: str) -> str:
        ...
    
    def exists(self, path: str) -> bool:
        ...
    
    def stat(self, path: str) -> dict:
        ...
    
    def get_file_size(self, path: str) -> int:
        ...
    
    def directory_summary(self, path: str) -> DirectorySummary:
        ...
    
    def get_server_info(self) -> dict:
        return {"type": "my_cloud", "config": self.config}
    
    def get_connection_string(self) -> str:
        return f"my_cloud://{self.config.get('bucket', 'unknown')}"
```

### Step 2: Create Plugin Registration

```python
# my_plugin/__init__.py
from dav_platform.core.contracts import IDataSource
from my_plugin.data_source import MyCloudDataSource

PLUGIN_NAME = "my_cloud"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "My Cloud data source connector"

def get_data_source(config: dict) -> IDataSource:
    """Factory function that returns an IDataSource instance."""
    return MyCloudDataSource(config)

__all__ = ["PLUGIN_NAME", "PLUGIN_VERSION", "PLUGIN_DESCRIPTION", "get_data_source"]
```

### Step 3: Install Plugin

Place the plugin in the `plugins/` directory:

```
plugins/
  my_plugin/
    __init__.py
    data_source.py
    requirements.txt
```

### Step 4: Register in Application

Add to connection service's source type registry:

```python
# In ui/services/connection_service.py
from plugins.my_plugin import get_data_source

# During initialization
self._source_types["my_cloud"] = get_data_source
```

## Creating a Validation Plugin

Custom validation rules can be added to extend data quality checking.

```python
# my_validation_plugin/rules.py
from dav_platform.core.contracts import ValidationRule, ValidationIssue, ValidationSeverity
import polars as pl

class CrossColumnValidation:
    """Validate relationships between columns."""
    
    @staticmethod
    def validate(df: pl.DataFrame, rule: ValidationRule) -> list[ValidationIssue]:
        issues = []
        if "price" in df.columns and "sales" in df.columns:
            # Check that price * quantity roughly equals sales
            ratio = (df["sales"] / (df["price"] + 1)).alias("ratio")
            violations = df.filter(ratio < 0.9)
            if violations.height > 0:
                issues.append(ValidationIssue(
                    rule=rule.name,
                    message=f"Found {violations.height} rows where sales don't match price * quantity",
                    severity=ValidationSeverity.WARNING,
                    row_count=violations.height,
                ))
        return issues
```

## Creating an Export Plugin

Custom export formats can be added by implementing an export handler.

```python
# my_export_plugin/exporter.py
import polars as pl
from pathlib import Path

class ParquetExporter:
    """Export data as Apache Parquet files."""
    
    @staticmethod
    def export(df: pl.DataFrame, output_path: str, options: dict = None) -> dict:
        path = Path(output_path) / f"export.parquet"
        df.write_parquet(str(path))
        return {
            "format": "parquet",
            "file": str(path),
            "size_bytes": path.stat().st_size,
            "rows": df.height,
        }
    
    @staticmethod
    def get_options() -> dict:
        return {
            "compression": {
                "type": "select",
                "values": ["snappy", "gzip", "lz4", "zstd"],
                "default": "snappy",
            },
            "row_group_size": {
                "type": "number",
                "default": 100000,
                "min": 1000,
                "max": 10000000,
            },
        }
```

## Creating a Theme Plugin

Custom UI themes can be added.

```python
# my_theme_plugin/theme.py
THEME_NAME = "ocean"
THEME_LABEL = "Ocean Blue"

css_vars = """
--bg-primary: #0a1628;
--bg-secondary: #0f1f3d;
--bg-card: #152a4a;
--text-primary: #e0f0ff;
--text-secondary: #80b0e0;
--accent: #00bcd4;
--accent-hover: #26c6da;
--border: #1a3366;
--success: #00e676;
--warning: #ffab00;
--error: #ff1744;
"""

def apply_theme(ui):
    ui.dark_mode().enable()
    ui.add_head_html(f"<style>:root {{{css_vars}}}</style>")
```

## Plugin Best Practices

### Plugin Structure

```
my_plugin/
  __init__.py          # Plugin metadata and factory functions
  requirements.txt     # Additional dependencies
  README.md           # Plugin documentation
  *.py                # Implementation modules
```

### Plugin Metadata

Every plugin should expose:

```python
PLUGIN_NAME = "unique_plugin_id"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Human-readable description"
PLUGIN_AUTHOR = "Author Name"
PLUGIN_LICENSE = "MIT"
PLUGIN_REQUIRES = ["dependency1>=1.0", "dependency2"]
```

### Guidelines

1. **Isolation** — Plugins should not modify core platform state directly
2. **Error Handling** — Catch and report errors gracefully; never crash the host application
3. **Dependencies** — List all dependencies in `requirements.txt`; use version pinning
4. **Documentation** — Include README with installation and usage instructions
5. **Testing** — Include tests for your plugin
6. **Versioning** — Follow semantic versioning for plugin releases
7. **Compatibility** — Test against the target DVA Platform version

### Plugin Registration

For production deployment, plugins can be registered through the central plugin registry:

```python
# plugins/registry.py
class PluginRegistry:
    _instance = None
    _plugins = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, name: str, plugin: dict) -> None:
        self._plugins[name] = plugin
    
    def get(self, name: str) -> dict:
        return self._plugins.get(name)
    
    def list_available(self) -> list[str]:
        return list(self._plugins.keys())
    
    def get_by_type(self, extension_type: str) -> list[dict]:
        return [
            p for p in self._plugins.values()
            if p.get("type") == extension_type
        ]
```

## Packaging and Distribution

### Directory Structure for Distribution

```
my-plugin-v1.0.0/
  my_plugin/
    __init__.py
    implementation.py
  requirements.txt
  README.md
  LICENSE
  setup.py
```

### setup.py Example

```python
from setuptools import setup, find_packages

setup(
    name="dva-plugin-my-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "dva-platform>=2.0.0",
    ],
    entry_points={
        "dva.plugins": [
            "my_plugin = my_plugin",
        ],
    },
)
```

## Troubleshooting Plugins

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Plugin not detected | Wrong directory structure | Ensure plugin is in `plugins/` directory |
| Import error | Missing dependencies | Install dependencies from `requirements.txt` |
| Compatibility error | Version mismatch | Check DVA Platform version compatibility |
| Performance issues | Inefficient implementation | Profile and optimize plugin code |
| UI not showing | Theme registration failed | Verify `apply_theme()` signature |

### Debugging Plugins

```bash
# Check plugin loading logs
tail -f ~/.dva/logs/dva.log | grep plugin

# Test plugin in isolation
python3 -c "from plugins.my_plugin import get_data_source; print('OK')"
```

## API Reference

### Extension Point Interfaces

| Interface | Module | Method Requirements |
|-----------|--------|-------------------|
| `IDataSource` | `dav_platform.core.contracts` | `connect()`, `disconnect()`, `list_directory()`, `read_sample()`, `open_stream()`, `download_if_required()`, `exists()`, `stat()`, `get_file_size()`, `directory_summary()`, `get_server_info()`, `get_connection_string()` |
| `ValidationRule` | `dav_platform.core.contracts` | `name`, `rule_type`, `severity`, `validate(df, config) -> list[ValidationIssue]` |
| `AggregationStrategy` | `dav_platform.core.contracts` | Enum value with registered aggregation function |
| `OutputFormat` | `dav_platform.core.contracts` | Enum value with registered export handler |

For questions about plugin development, refer to the [Developer Guide](developer_guide.md) or contact the development team.
