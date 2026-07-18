"""Output Layer — Exceptions."""


class OutputEngineError(Exception):
    """Base error for output operations."""


class ExportError(OutputEngineError):
    """A file export failed."""


class ConfigurationError(OutputEngineError):
    """Invalid output configuration."""


class ReportBuildError(OutputEngineError):
    """Report generation failed."""


class FormatNotSupportedError(OutputEngineError):
    """Requested output format is not supported."""


class MissingInputError(OutputEngineError):
    """Required input data is missing."""
