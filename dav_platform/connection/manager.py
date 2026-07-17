"""Connection manager for data sources."""

import logging
from typing import Optional

from dav_platform.core.contracts import IDataSource, DataSourceError
from dav_platform.connection.local import LocalDataSource
from dav_platform.connection.ssh import SSHDataSource

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages data source connections.

    Creates and configures IDataSource instances based on connection type.
    """

    @staticmethod
    def create_local() -> LocalDataSource:
        return LocalDataSource()

    @staticmethod
    def create_ssh(
        host: str,
        port: int = 22,
        username: str = "",
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        key_passphrase: Optional[str] = None,
        timeout: int = 15,
    ) -> SSHDataSource:
        return SSHDataSource(
            host=host,
            port=port,
            username=username,
            password=password,
            key_file=key_file,
            key_passphrase=key_passphrase,
            timeout=timeout,
        )

    @staticmethod
    def connect(source: IDataSource) -> bool:
        """Connect to a data source."""
        try:
            return source.connect()
        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(f"Connection failed: {e}")

    @staticmethod
    def disconnect(source: IDataSource) -> None:
        """Disconnect from a data source."""
        try:
            source.disconnect()
        except Exception as e:
            logger.warning("Disconnect error: %s", e)
