"""Output Layer — Presentation and Export Engine.

Converts validated business results into consumable artifacts.
Performs NO aggregation, NO calculation, NO validation.
"""

from dav_platform.output.csv_export import CSVExporter
from dav_platform.output.engine import OutputEngine
from dav_platform.output.excel import ExcelExporter
from dav_platform.output.exceptions import (
    ConfigurationError,
    ExportError,
    FormatNotSupportedError,
    MissingInputError,
    OutputEngineError,
    ReportBuildError,
)
from dav_platform.output.manifest import ManifestBuilder
from dav_platform.output.metadata import OutputMetadataCollector
from dav_platform.output.reports import ReportBuilder
from dav_platform.output.statistics import OutputStatisticsEngine
from dav_platform.output.templates import (
    BottomStoresTemplate,
    BusinessStatisticsTemplate,
    CategorySummaryTemplate,
    DashboardSummaryTemplate,
    ExecutionSummaryTemplate,
    MetadataTemplate,
    ReportTemplate,
    StoreValidationSummaryTemplate,
    TEMPLATE_REGISTRY,
    TopStoresByQuantityTemplate,
    TopStoresBySalesTemplate,
    ValidationSummaryTemplate,
    register_template,
)
from dav_platform.output.configuration import OutputConfigBuilder, build_output_config

__all__ = [
    "OutputEngine",
    "ReportBuilder",
    "ExcelExporter",
    "CSVExporter",
    "ManifestBuilder",
    "OutputMetadataCollector",
    "OutputStatisticsEngine",
    "OutputConfigBuilder",
    "build_output_config",
    "ReportTemplate",
    "ValidationSummaryTemplate",
    "StoreValidationSummaryTemplate",
    "TopStoresBySalesTemplate",
    "TopStoresByQuantityTemplate",
    "BottomStoresTemplate",
    "CategorySummaryTemplate",
    "BusinessStatisticsTemplate",
    "ExecutionSummaryTemplate",
    "MetadataTemplate",
    "DashboardSummaryTemplate",
    "TEMPLATE_REGISTRY",
    "register_template",
    "OutputEngineError",
    "ExportError",
    "ConfigurationError",
    "ReportBuildError",
    "FormatNotSupportedError",
    "MissingInputError",
]
