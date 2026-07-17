"""Unit tests for ConnectionManager."""

import pytest

from dav_platform.connection.manager import ConnectionManager
from dav_platform.connection.local import LocalDataSource
from dav_platform.core.contracts import DataSourceError


class TestConnectionManager:
    def test_create_local(self):
        source = ConnectionManager.create_local()
        assert isinstance(source, LocalDataSource)

    def test_connect_local(self):
        source = ConnectionManager.create_local()
        result = ConnectionManager.connect(source)
        assert result is True

    def test_disconnect_local(self):
        source = ConnectionManager.create_local()
        ConnectionManager.connect(source)
        ConnectionManager.disconnect(source)
        assert source.is_connected is True
