"""Output Layer — Configuration Builder."""

from typing import Any, Dict, List, Optional

from dav_platform.core.contracts import OutputConfig


class OutputConfigBuilder:
    """Builder for OutputConfig objects."""

    def __init__(self):
        self._output_dir = "./output"
        self._excel_enabled = True
        self._csv_enabled = True
        self._json_enabled = True
        self._include_validation_summary = True
        self._include_store_summary = True
        self._include_upc_summary = True
        self._include_category_summary = True
        self._include_brand_summary = True
        self._include_department_summary = True
        self._include_business_kpis = True
        self._include_processing_summary = True
        self._include_execution_summary = True
        self._include_metadata_sheet = True
        self._include_dashboard = True
        self._max_top_stores = 5
        self._max_bottom_stores = 5
        self._metadata: Dict[str, Any] = {}

    def output_dir(self, path: str) -> "OutputConfigBuilder":
        self._output_dir = path
        return self

    def excel(self, enabled: bool = True) -> "OutputConfigBuilder":
        self._excel_enabled = enabled
        return self

    def csv(self, enabled: bool = True) -> "OutputConfigBuilder":
        self._csv_enabled = enabled
        return self

    def json(self, enabled: bool = True) -> "OutputConfigBuilder":
        self._json_enabled = enabled
        return self

    def validation_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_validation_summary = include
        return self

    def store_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_store_summary = include
        return self

    def upc_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_upc_summary = include
        return self

    def category_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_category_summary = include
        return self

    def brand_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_brand_summary = include
        return self

    def department_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_department_summary = include
        return self

    def business_kpis(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_business_kpis = include
        return self

    def processing_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_processing_summary = include
        return self

    def execution_summary(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_execution_summary = include
        return self

    def metadata_sheet(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_metadata_sheet = include
        return self

    def dashboard(self, include: bool = True) -> "OutputConfigBuilder":
        self._include_dashboard = include
        return self

    def max_top_stores(self, n: int) -> "OutputConfigBuilder":
        self._max_top_stores = n
        return self

    def max_bottom_stores(self, n: int) -> "OutputConfigBuilder":
        self._max_bottom_stores = n
        return self

    def metadata(self, key: str, value: Any) -> "OutputConfigBuilder":
        self._metadata[key] = value
        return self

    def build(self) -> OutputConfig:
        return OutputConfig(
            output_dir=self._output_dir,
            excel_enabled=self._excel_enabled,
            csv_enabled=self._csv_enabled,
            json_enabled=self._json_enabled,
            include_validation_summary=self._include_validation_summary,
            include_store_summary=self._include_store_summary,
            include_upc_summary=self._include_upc_summary,
            include_category_summary=self._include_category_summary,
            include_brand_summary=self._include_brand_summary,
            include_department_summary=self._include_department_summary,
            include_business_kpis=self._include_business_kpis,
            include_processing_summary=self._include_processing_summary,
            include_execution_summary=self._include_execution_summary,
            include_metadata_sheet=self._include_metadata_sheet,
            include_dashboard=self._include_dashboard,
            max_top_stores=self._max_top_stores,
            max_bottom_stores=self._max_bottom_stores,
            metadata=self._metadata,
        )


def build_output_config(
    output_dir: str = "./output",
    excel: bool = True,
    csv: bool = True,
    json: bool = True,
    **kwargs,
) -> OutputConfig:
    """Convenience function to build an OutputConfig."""
    builder = OutputConfigBuilder()
    builder.output_dir(output_dir)
    builder.excel(excel)
    builder.csv(csv)
    builder.json(json)
    return builder.build()
