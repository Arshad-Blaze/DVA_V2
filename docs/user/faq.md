# Frequently Asked Questions — DVA Platform v2

## General

### What is DVA Platform?

DVA Platform v2 is a retail data processing platform that ingests raw retail data files, automatically detects their structure, transforms them into a standardized format, and executes configurable processing workflows including aggregation, calculation, validation, and reporting.

### Who is DVA Platform for?

The platform is designed for retail data analysts, data engineers, and business intelligence professionals who need to process and analyze retail data from diverse sources and formats.

### What file formats are supported?

The platform supports delimited files (CSV, TSV, pipe-delimited, etc.), fixed-width files, multiline records, mixed-record files, and Excel files (.xlsx). Output can be exported as Excel, CSV, or JSON.

### What makes DVA different from using Polars or Pandas directly?

DVA provides automatic file structure detection, intelligent column role mapping, canonical transformation, execution workflow orchestration, built-in validation, and a graphical user interface — all on top of Polars. It handles the repetitive parts of retail data processing so you can focus on analysis.

### Which Python version is required?

Python 3.12 or later is required. Python 3.13 is also supported. Python 3.11 and earlier are not supported.

## Installation and Setup

### How do I install DVA Platform?

See the [Quick Start Guide](quick_start_guide.md) for installation steps, or the [Installation Guide](installation_guide.md) for production setup instructions.

### Can I run DVA in a Docker container?

Yes. See the [Administrator Guide](administrator_guide.md) for Docker deployment instructions including a Dockerfile and Docker Compose configuration.

### Does DVA require a database?

No. DVA uses local file system storage (`~/.dva/`) for all persistent state. No external database is required.

### Can I run DVA on Windows?

Yes. Windows 10 and Windows 11 are supported. File paths must use forward slashes or escaped backslashes.

### Can I run DVA on macOS?

macOS is supported but not officially tested. Intel Macs and Apple Silicon Macs (via Rosetta 2) should work with the community-supported configuration.

## Usage

### How do I start the application?

Run `python3 -m ui.app` from the project directory, then open http://localhost:8080 in your browser.

### How do I change the theme?

Go to the **Settings** workspace and select your preferred theme: Light, Dark, High Contrast, or System (follows OS setting). You can also use `Ctrl+D` to toggle dark mode.

### How many projects can I have?

There is no hard limit, but performance may degrade with more than 50 active projects. The default maximum is configurable in `~/.dva/config.json`.

### Can I process multiple files at once?

Currently, the platform processes one file or dataset at a time through the pipeline. Batch processing is planned for a future release.

### How do I export my results?

Navigate to the **Reports** workspace after processing, select your desired export format (Excel, CSV, JSON), and click Export. Files are saved to your configured output directory.

### Can I schedule recurring processing?

Scheduled/automated processing is not available in v2.0.0. This is planned for a future release.

## Data and Processing

### What is the maximum file size I can process?

The default maximum file size is 1GB. This can be increased via the `DVA_MAX_FILE_SIZE` environment variable. For files over 1GB, streaming mode is strongly recommended.

### How does the platform handle encoding?

The Detection layer automatically detects file encoding (UTF-8, UTF-16, Latin-1, ANSI). You can manually override the detected encoding if needed.

### What happens to my data?

All data remains on your local system. The platform reads data from your specified sources, processes it in memory or via temporary files, and writes results to your specified output directory. No data is transmitted externally.

### How does the Quantity Intelligence feature work?

The Detection layer analyzes numeric columns to identify quantity-related fields. It distinguishes between weighted quantity (e.g., pounds, kilograms) and unit count (e.g., individual items). The recommendation is based on data distribution analysis and column name heuristics.

### Can I add custom columns during processing?

Yes. The Processing layer supports calculations that create derived columns using expressions. You can define calculations in the Operation or Processing workspace.

## Troubleshooting

### The application won't start. What should I do?

1. Run `python3 scripts/dependency_checker.py` to verify all dependencies
2. Run `python3 scripts/environment_validation.py` to check system prerequisites
3. Run `python3 scripts/startup_validation.py` for a comprehensive pre-launch check
4. Check that port 8080 is available

### My data shows garbled characters. What's wrong?

This is typically an encoding issue. Try manually selecting a different encoding (UTF-8, Latin-1, or Windows-1252) in the Detection workspace.

### Processing is very slow for large files. How can I improve performance?

Enable streaming mode, adjust chunk size, disable statistics computation, and ensure you're using Polars-native operations. See the [Troubleshooting Guide](troubleshooting_guide.md) for detailed performance optimization steps.

### How do I clear the cache?

Go to **Administration** workspace → Cache Management → Clear Cache. You can also manually delete `~/.dva/cache/`.

### Where are logs stored?

Application logs are stored in `~/.dva/logs/dva.log`. The log level is configurable via the `DVA_LOG_LEVEL` environment variable.

## Support and Maintenance

### How do I back up my data?

Copy the `~/.dva/` directory. This contains all projects, connections, settings, and session state. See the [Administrator Guide](administrator_guide.md) for detailed backup procedures.

### How do I update DVA to a newer version?

Pull the latest code from the repository and reinstall dependencies. See the [Administrator Guide](administrator_guide.md) for the complete upgrade procedure.

### Can I use DVA behind a reverse proxy?

Yes. DVA can be deployed behind nginx, Apache, or any reverse proxy that supports HTTP proxying. Configure your proxy to forward requests to `http://localhost:8080`.

### How do I report a bug?

Report bugs to the development team with:
- DVA Platform version
- Operating system and Python version
- Steps to reproduce
- Full error message and stack trace
- Log files from `~/.dva/logs/`

### Is there a roadmap for future features?

Yes. See the [Future Roadmap](../release/future_roadmap.md) for planned features and development priorities.

## Technical

### What is the technology stack?

- **Frontend**: NiceGUI (Python web UI framework)
- **Data Processing**: Polars (DataFrame library)
- **Storage**: Local file system (JSON-based persistence)
- **Temporary Storage**: DuckDB (for streaming/chunked operations)
- **Columnar Format**: Apache Arrow (via PyArrow)

### Is there an API?

DVA Platform v2 is primarily a GUI application. There is no REST API in v2.0.0. A programmatic API is planned for a future release.

### Can I extend the platform with custom functionality?

Yes. DVA supports plugins for data sources, validation rules, export formats, UI themes, and more. See the [Plugin Guide](../developer/plugin_guide.md) for details.

### Does DVA support multi-user mode?

Basic multi-user support is available through the Administration workspace for user management. Full multi-tenancy is planned for a future release.

### What data privacy measures are in place?

All data processing happens locally. No data is sent to external servers. File paths are validated to prevent traversal attacks. Session data is stored in the user's home directory with restricted permissions.
