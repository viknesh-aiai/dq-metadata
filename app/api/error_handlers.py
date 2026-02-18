from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DQMetadataException, TableNotFoundException, DatabaseError
from app.core.logging import logger


async def dq_metadata_exception_handler(request: Request, exc: DQMetadataException):
    """
    Generic handler for app-specific logic errors.
    """
    logger.error("DQ Metadata Exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal service error", "error_code": "INTERNAL_ERROR"},
    )


async def table_not_found_handler(request: Request, exc: TableNotFoundException):
    """
    Handle 404s for missing metadata.
    """
    logger.info("Table not found", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "error_code": "TABLE_NOT_FOUND"},
    )


async def database_error_handler(request: Request, exc: DatabaseError):
    """
    Handle DB connection issues or query failures.
    """
    logger.error("Database Error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service unavailable", "error_code": "DB_ERROR"},
    )
