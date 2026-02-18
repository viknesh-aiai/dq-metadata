from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import TableNotFoundException, DatabaseError, DQMetadataException
from app.api.error_handlers import (
    table_not_found_handler,
    database_error_handler,
    dq_metadata_exception_handler
)
from app.api import endpoints
from app.core.heuristics import HeuristicsLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting dq-metadata service", env=settings.ENV)
    try:
        # Pre-load heuristics to fail fast if config is invalid
        HeuristicsLoader.get_instance()
        logger.info("Heuristics loaded successfully")
    except Exception as e:
        logger.critical("Failed to initialize service", error=str(e))
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down dq-metadata service")


def create_app() -> FastAPI:
    setup_logging()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(endpoints.router, prefix="/metadata", tags=["Metadata"])

    # Error Handlers
    app.add_exception_handler(TableNotFoundException, table_not_found_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
    app.add_exception_handler(DQMetadataException, dq_metadata_exception_handler)

    return app


app = create_app()
