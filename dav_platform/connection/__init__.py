"""Data Access Layer - Connection module.

Responsibilities:
- Connect / Disconnect
- Browse directories
- Read files (sample, stream, download)
- Return IDataSource

Nothing else.
"""

from dav_platform.connection.local import LocalDataSource
from dav_platform.connection.ssh import SSHDataSource
from dav_platform.connection.manager import ConnectionManager

__all__ = ["LocalDataSource", "SSHDataSource", "ConnectionManager"]
