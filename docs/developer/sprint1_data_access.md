# Sprint 1: Data Access Layer

## Responsibilities

- Connect / Disconnect
- Browse directories
- Read files (sample, stream, download)
- Get file metadata (size, summary)
- Return IDataSource

Nothing else.

## Contract

`IDataSource` defines the interface:

```python
class IDataSource(ABC):
    # Connection
    def connect(self) -> bool: ...
    def disconnect(self) -> None: ...
    def is_connected(self) -> bool: ...
    supports_direct_path: bool  # property

    # Browse
    def list_directory(self, path: str) -> List[DataSourceEntry]: ...
    def list_files(self, path: str) -> List[str]: ...

    # Read
    def read_sample(self, path: str, n: int = 100) -> str: ...
    def open_stream(self, path: str) -> BinaryIO: ...
    def download_if_required(self, path: str) -> str: ...

    # Metadata
    def exists(self, path: str) -> bool: ...
    def stat(self, path: str) -> dict: ...
    def get_file_size(self, path: str) -> int: ...
    def directory_summary(self, path: str) -> DirectorySummary: ...
    def get_server_info(self) -> dict: ...
    def get_connection_string(self) -> str: ...
```

## Data Types

- `DataSourceEntry` - File/directory metadata
- `DirectorySummary` - Aggregate statistics for adaptive access strategy
- `DataSourceError` - Consistent error type across all connectors

## Implementations

- `LocalDataSource` - Local filesystem
- `SSHDataSource` - Remote SSH/SFTP
- `ConnectionManager` - Factory for creating connectors

## Future Connectors (no IDataSource changes required)

- SFTP (extends SSHDataSource pattern)
- MFT (Managed File Transfer)
- Azure Blob Storage
- AWS S3
- Google Cloud Storage
- FTP

## Extension Points

To add a new connector:
1. Implement `IDataSource`
2. Use `DataSourceError` for all exceptions
3. Return `DataSourceEntry` / `DirectorySummary` for metadata
4. Support `open_stream()` for streaming reads

## Sequence Diagram

```
User -> ConnectionManager -> IDataSource -> Data Source
                              |
                              +-> connect()
                              +-> list_directory()
                              +-> read_sample()
                              +-> open_stream()
                              +-> get_file_size()
                              +-> directory_summary()
                              +-> disconnect()
```

## Data Flow

```
ConnectionManager.create_local()
    -> LocalDataSource()
    -> .connect()
    -> .list_directory() / .read_sample() / .open_stream()
    -> .disconnect()
```

## Known Limitations

- `download_if_required()` creates temp files for SSH (cleanup responsibility TBD)
- No automatic reconnection on connection loss
- No connection pooling (future enhancement)

## Future Sprint Integration

- Sprint 2 (Detection): Consumes `IDataSource.read_sample()` and `open_stream()`
- Sprint 3 (Canonical): Uses `IDataSource.open_stream()` for streaming
- Sprint 5 (Operations): Uses `directory_summary()` for adaptive strategy
- Sprint 9 (Cleanup): Handles temp file cleanup from SSH downloads

## Test Coverage

39 unit tests covering:
- LocalDataSource: 28 tests
- ConnectionManager: 3 tests
- Core contracts: 8 tests

All tests pass.
