class DQMetadataException(Exception):
    """Base exception for dq-metadata service"""
    pass


class ConfigurationError(DQMetadataException):
    """Raised when configuration is invalid or missing"""
    pass


class DatabaseError(DQMetadataException):
    """Raised when database operations fail"""
    pass


class TableNotFoundException(DQMetadataException):
    """Raised when a requested table is not found in metadata"""
    pass


class HeuristicsError(DQMetadataException):
    """Raised when heuristics loading or application fails"""
    pass
