"""Tests — Output Layer: Configuration."""

from dav_platform.core.contracts import OutputConfig
from dav_platform.output.configuration import OutputConfigBuilder, build_output_config


class TestOutputConfigBuilder:
    def test_default_config(self):
        config = OutputConfigBuilder().build()
        assert isinstance(config, OutputConfig)
        assert config.output_dir == "./output"
        assert config.excel_enabled is True
        assert config.csv_enabled is True
        assert config.json_enabled is True
        assert config.include_validation_summary is True
        assert config.include_store_summary is True
        assert config.include_upc_summary is True
        assert config.max_top_stores == 5
        assert config.max_bottom_stores == 5

    def test_custom_output_dir(self):
        config = OutputConfigBuilder().output_dir("/tmp/reports").build()
        assert config.output_dir == "/tmp/reports"

    def test_disable_excel(self):
        config = OutputConfigBuilder().excel(False).build()
        assert config.excel_enabled is False

    def test_disable_csv(self):
        config = OutputConfigBuilder().csv(False).build()
        assert config.csv_enabled is False

    def test_disable_json(self):
        config = OutputConfigBuilder().json(False).build()
        assert config.json_enabled is False

    def test_custom_top_stores(self):
        config = OutputConfigBuilder().max_top_stores(10).build()
        assert config.max_top_stores == 10

    def test_custom_bottom_stores(self):
        config = OutputConfigBuilder().max_bottom_stores(3).build()
        assert config.max_bottom_stores == 3

    def test_include_flags(self):
        config = (
            OutputConfigBuilder()
            .validation_summary(False)
            .store_summary(False)
            .category_summary(True)
            .business_kpis(True)
            .execution_summary(False)
            .dashboard(False)
            .build()
        )
        assert config.include_validation_summary is False
        assert config.include_store_summary is False
        assert config.include_category_summary is True
        assert config.include_business_kpis is True
        assert config.include_execution_summary is False
        assert config.include_dashboard is False

    def test_metadata(self):
        config = OutputConfigBuilder().metadata("version", "2.0").build()
        assert config.metadata["version"] == "2.0"

    def test_chained_fluent_builder(self):
        config = (
            OutputConfigBuilder()
            .output_dir("./reports")
            .excel(True)
            .csv(False)
            .json(True)
            .validation_summary(True)
            .store_summary(True)
            .max_top_stores(10)
            .build()
        )
        assert config.output_dir == "./reports"
        assert config.excel_enabled is True
        assert config.csv_enabled is False
        assert config.max_top_stores == 10


class TestBuildOutputConfig:
    def test_convenience_defaults(self):
        config = build_output_config()
        assert config.output_dir == "./output"
        assert config.excel_enabled is True
        assert config.csv_enabled is True
        assert config.json_enabled is True

    def test_convenience_custom(self):
        config = build_output_config(output_dir="/tmp", excel=False, csv=True, json=False)
        assert config.output_dir == "/tmp"
        assert config.excel_enabled is False
        assert config.csv_enabled is True
        assert config.json_enabled is False
