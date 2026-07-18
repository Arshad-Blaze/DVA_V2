"""Tests — Flush Layer: Configuration."""

from dav_platform.core.contracts import FlushConfig
from dav_platform.flush.configuration import FlushConfigBuilder, build_flush_config


class TestFlushConfigBuilder:
    def test_default_config(self):
        config = FlushConfigBuilder().build()
        assert isinstance(config, FlushConfig)
        assert config.retain_temp_files is False
        assert config.retain_logs is False
        assert config.retain_caches is False
        assert config.delete_exports is False
        assert config.archive_reports is False
        assert config.verbose is False
        assert config.dry_run is False
        assert config.temp_directories == []
        assert config.cache_keys == []

    def test_retain_temp_files(self):
        config = FlushConfigBuilder().retain_temp_files().build()
        assert config.retain_temp_files is True

    def test_retain_logs(self):
        config = FlushConfigBuilder().retain_logs().build()
        assert config.retain_logs is True

    def test_dry_run(self):
        config = FlushConfigBuilder().dry_run().build()
        assert config.dry_run is True

    def test_add_temp_directory(self):
        config = FlushConfigBuilder().add_temp_directory("/tmp/foo").build()
        assert "/tmp/foo" in config.temp_directories

    def test_add_cache_key(self):
        config = FlushConfigBuilder().add_cache_key("my_cache").build()
        assert "my_cache" in config.cache_keys

    def test_verbose(self):
        config = FlushConfigBuilder().verbose(True).build()
        assert config.verbose is True

    def test_delete_exports(self):
        config = FlushConfigBuilder().delete_exports(True).build()
        assert config.delete_exports is True

    def test_chained_builder(self):
        config = (
            FlushConfigBuilder()
            .retain_temp_files()
            .retain_caches()
            .dry_run()
            .add_temp_directory("/tmp/data")
            .build()
        )
        assert config.retain_temp_files is True
        assert config.retain_caches is True
        assert config.dry_run is True
        assert config.temp_directories == ["/tmp/data"]


class TestBuildFlushConfig:
    def test_convenience_defaults(self):
        config = build_flush_config()
        assert config.retain_temp_files is False
        assert config.dry_run is False

    def test_convenience_custom(self):
        config = build_flush_config(retain_temp_files=True, dry_run=True)
        assert config.retain_temp_files is True
        assert config.dry_run is True
