# Known Limitations — DVA Platform v2.0.0

This document lists known limitations, constraints, and non-goals for DVA Platform v2.0.0. These are areas identified for improvement in future releases.

## Functional Limitations

### Single File Processing
The platform processes one file or dataset at a time through the pipeline. Batch processing of multiple files in parallel is not supported. Users must process files individually and combine results manually.

### No Real-Time Processing
DVA Platform is designed for batch processing of static data files. Real-time streaming data ingestion and processing are not supported.

### No REST API
v2.0.0 is a GUI-only application with no programmatic API. External systems cannot interact with DVA Platform programmatically. All processing must be initiated through the web interface.

### No Scheduled Execution
Automated or scheduled workflow execution is not supported. All processing must be manually initiated by a user through the UI.

### Limited Multi-User Support
While basic user management is available in the Administration workspace, the platform does not provide true multi-tenancy with isolated user environments, role-based access control, or concurrent user session management.

### No Authentication
The application does not include built-in authentication or authorization. All users with network access to the application port can use the platform. For production deployments, use a reverse proxy with authentication.

### No HTTPS
The application runs on HTTP by default. HTTPS is not supported natively. Use a reverse proxy (nginx, Apache) for TLS termination in production environments.

## Data Limitations

### Maximum File Size
The default maximum file size is 1GB. While this is configurable, files exceeding 2GB may cause memory issues depending on available system resources. Streaming mode is recommended for files over 100MB.

### Column Count Limit
While there is no hard limit on column count, detection performance may degrade with files containing more than 200 columns. Column role detection accuracy may decrease with large numbers of candidate columns.

### Unicode Support
The platform supports UTF-8, UTF-16, Latin-1, and ANSI encodings. Other encodings (EBCDIC, ISO-2022, etc.) may not be detected correctly. Users should convert files to supported encodings before processing.

### Excel Limitations
- Only .xlsx files are supported (not .xls)
- Maximum sheet size limited by openpyxl (1,048,576 rows)
- Excel files with complex formatting, macros, or embedded objects may not parse correctly
- Password-protected Excel files are not supported

### No Database Connectivity
The platform cannot connect directly to databases (SQL, NoSQL). Data must be exported to files before processing with DVA Platform.

## Platform Limitations

### Python 3.12+ Only
The platform requires Python 3.12 or later. Python 3.11 and earlier versions are not supported. Users on older Python versions must upgrade.

### Memory-Bound Processing
Processing performance is primarily limited by available system memory. Processing very large files on memory-constrained systems may fail or be extremely slow.

### Single-Threaded UI
The NiceGUI application runs in a single process. CPU-intensive processing operations can temporarily block the UI. Future versions may offload processing to worker threads or processes.

### No Horizontal Scaling
The platform runs as a single instance and cannot be clustered or scaled horizontally. For high-throughput scenarios, consider running multiple instances with separate data directories.

### Limited Plugin Discovery
Plugins must be manually placed in the `plugins/` directory and registered in the codebase. Automatic plugin discovery and loading are not implemented.

## UI Limitations

### No Mobile Responsiveness
The UI is designed for desktop screen sizes (1024px minimum width). Mobile browsers and small screens are not supported.

### No Accessibility Features
The interface does not include screen reader optimizations, keyboard navigation enhancements, or other accessibility features beyond standard browser capabilities.

### No Internationalization
The UI is available in English only. No translations or locale-specific formatting are provided.

### No Drag-and-Drop
File selection and workspace organization do not support drag-and-drop interactions. Users must use browse dialogs and button clicks.

## Known Bugs

### Detection
- Files with mixed line endings (CR+LF and LF) may have incorrect line counts
- Very short files (< 10 lines) may have reduced detection accuracy
- Files without headers and with only numeric data may have false positive header detection

### Canonical Mapping
- Column role detection may misidentify short numeric codes (e.g., "1", "2") as quantity columns
- Single-character column names reduce mapping confidence

### Processing
- Streaming mode with calculations may produce different row ordering than non-streaming mode
- Division by zero in calculations produces null values instead of configurable defaults

### Export
- Excel export may fail for datasets exceeding 500,000 rows due to openpyxl limitations
- Excel dashboard charts may not render correctly in LibreOffice Calc

## Non-Goals

The following features are explicitly out of scope for v2.0.0:

- Real-time streaming data processing
- Machine learning or predictive analytics
- Data visualization beyond basic export dashboards
- Cloud-native deployment (Kubernetes, serverless)
- Data warehousing or long-term data storage
- ETL scheduling or orchestration
- Native mobile applications
- REST or GraphQL API
- User authentication and authorization
- Horizontal scaling or clustering
- Database connectivity
- Multi-language support
- Accessibility compliance

## Future Improvements

These limitations are addressed in the [Future Roadmap](future_roadmap.md). Planned enhancements include batch processing, REST API, scheduled execution, and authentication support.

## Reporting Limitations

If you encounter a limitation not listed here, please report it to the development team with:
- Detailed description of the limitation
- Use case requiring the feature
- Workaround if any
- Impact on your workflow
