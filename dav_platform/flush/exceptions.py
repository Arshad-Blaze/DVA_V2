"""Flush Layer — Exceptions."""


class FlushEngineError(Exception):
    """Base error for flush operations."""


class CleanupError(FlushEngineError):
    """A cleanup operation failed."""


class ConfigurationError(FlushEngineError):
    """Invalid flush configuration."""


class ResourceCleanupError(FlushEngineError):
    """Resource cleanup failed."""


class ConnectionCleanupError(FlushEngineError):
    """Connection cleanup failed."""


class CacheCleanupError(FlushEngineError):
    """Cache cleanup failed."""


class SessionCleanupError(FlushEngineError):
    """Session cleanup failed."""
