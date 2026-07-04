"""Domain exceptions — typed errors for the application layer."""


class HealthCoverageError(Exception):
    """Base exception for all application errors."""


class AffiliateNotFoundError(HealthCoverageError):
    """Raised when an affiliate cannot be located in the database."""


class DatabaseConnectionError(HealthCoverageError):
    """Raised when the database is unreachable."""


class VectorStoreError(HealthCoverageError):
    """Raised when a vector store operation fails."""


class CoverageAnalysisError(HealthCoverageError):
    """Raised when the coverage analysis agent encounters an unrecoverable error."""


class NotImplementedYetError(HealthCoverageError):
    """Raised for features planned in future sprints."""
