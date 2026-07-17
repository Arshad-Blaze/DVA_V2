"""Unit tests for LocalDataSource."""

import os
import tempfile
import pytest

from dav_platform.connection.local import LocalDataSource
from dav_platform.core.contracts import DataSourceError, DataSourceEntry, DirectorySummary


@pytest.fixture
def local_source():
    return LocalDataSource()


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample CSV file."""
    csv_content = "name,price,quantity\nApple,1.50,100\nBanana,0.75,200\n"
    file_path = tmp_path / "sample.csv"
    file_path.write_text(csv_content)
    return str(file_path)


@pytest.fixture
def sample_dir(tmp_path):
    """Create a sample directory with files."""
    (tmp_path / "file1.csv").write_text("a,b,c\n")
    (tmp_path / "file2.txt").write_text("hello\n")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.csv").write_text("x,y,z\n")
    return str(tmp_path)


class TestLocalDataSource:
    def test_connect_always_succeeds(self, local_source):
        assert local_source.connect() is True

    def test_is_connected_always_true(self, local_source):
        assert local_source.is_connected is True

    def test_supports_direct_path(self, local_source):
        assert local_source.supports_direct_path is True

    def test_disconnect_noop(self, local_source):
        local_source.disconnect()
        assert local_source.is_connected is True

    def test_list_directory(self, local_source, sample_dir):
        entries = local_source.list_directory(sample_dir)
        assert len(entries) == 3
        assert all(isinstance(e, DataSourceEntry) for e in entries)
        names = [e.name for e in entries]
        assert "file1.csv" in names
        assert "file2.txt" in names
        assert "subdir" in names

    def test_list_directory_nonexistent_raises(self, local_source):
        with pytest.raises(DataSourceError):
            local_source.list_directory("/nonexistent/path/xyz")

    def test_list_files_single_file(self, local_source, sample_file):
        files = local_source.list_files(sample_file)
        assert len(files) == 1
        assert files[0] == sample_file

    def test_list_files_directory(self, local_source, sample_dir):
        files = local_source.list_files(sample_dir)
        assert len(files) == 3

    def test_list_files_nonexistent_raises(self, local_source):
        with pytest.raises(DataSourceError):
            local_source.list_files("/nonexistent/path/xyz")

    def test_read_sample(self, local_source, sample_file):
        content = local_source.read_sample(sample_file, n=2)
        lines = content.strip().split("\n")
        assert len(lines) == 2
        assert lines[0] == "name,price,quantity"

    def test_read_sample_empty_file(self, local_source, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        content = local_source.read_sample(str(empty_file))
        assert content == ""

    def test_open_stream(self, local_source, sample_file):
        stream = local_source.open_stream(sample_file)
        try:
            data = stream.read()
            assert b"Apple" in data
        finally:
            stream.close()

    def test_download_if_required_returns_same_path(self, local_source, sample_file):
        result = local_source.download_if_required(sample_file)
        assert result == os.path.abspath(sample_file)

    def test_exists_true(self, local_source, sample_file):
        assert local_source.exists(sample_file) is True

    def test_exists_false(self, local_source):
        assert local_source.exists("/nonexistent/file.txt") is False

    def test_stat_file(self, local_source, sample_file):
        info = local_source.stat(sample_file)
        assert "size" in info
        assert "modified" in info
        assert info["is_file"] is True
        assert info["is_dir"] is False

    def test_stat_directory(self, local_source, sample_dir):
        info = local_source.stat(sample_dir)
        assert info["is_dir"] is True
        assert info["is_file"] is False

    def test_stat_nonexistent_raises(self, local_source):
        with pytest.raises(DataSourceError):
            local_source.stat("/nonexistent/path/xyz")

    def test_get_file_size_file(self, local_source, sample_file):
        size = local_source.get_file_size(sample_file)
        assert size > 0
        assert size == os.path.getsize(sample_file)

    def test_get_file_size_directory_returns_zero(self, local_source, sample_dir):
        size = local_source.get_file_size(sample_dir)
        assert size == 0

    def test_get_file_size_nonexistent_returns_zero(self, local_source):
        size = local_source.get_file_size("/nonexistent/file.txt")
        assert size == 0

    def test_directory_summary(self, local_source, sample_dir):
        summary = local_source.directory_summary(sample_dir)
        assert isinstance(summary, DirectorySummary)
        assert summary.total_files == 2
        assert summary.total_size > 0
        assert summary.largest_file is not None
        assert summary.smallest_file is not None
        assert summary.average_file_size > 0
        assert ".csv" in summary.file_extensions
        assert ".txt" in summary.file_extensions
        assert summary.estimated_transfer_bytes == summary.total_size

    def test_directory_summary_nonexistent_raises(self, local_source):
        with pytest.raises(DataSourceError):
            local_source.directory_summary("/nonexistent/path/xyz")

    def test_directory_summary_file_raises(self, local_source, sample_file):
        with pytest.raises(DataSourceError):
            local_source.directory_summary(sample_file)

    def test_get_server_info(self, local_source):
        info = local_source.get_server_info()
        assert info["type"] == "local"
        assert "platform" in info

    def test_get_connection_string(self, local_source):
        cs = local_source.get_connection_string()
        assert cs == "Local File System"

    def test_streaming_read_chunked(self, local_source, sample_file):
        stream = local_source.open_stream(sample_file)
        try:
            chunk1 = stream.read(5)
            chunk2 = stream.read(5)
            assert len(chunk1) == 5
            assert len(chunk2) == 5
            assert chunk1 + chunk2 == b"name," + b"price"
        finally:
            stream.close()

    def test_read_sample_large_n(self, local_source, sample_file):
        content = local_source.read_sample(sample_file, n=1000)
        lines = content.strip().split("\n")
        assert len(lines) == 3
