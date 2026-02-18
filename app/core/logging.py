import logging
import sys
from typing import Any, Dict

import structlog
from app.core.config import settings


def setup_logging():
    """
    Configure structured logging for the application.
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.ENV == "production":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development mode - pretty printing
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to use structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer() if settings.ENV == "production" else structlog.dev.ConsoleRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    # Silence noisy libraries
    logging.getLogger("uvicorn.access").handlers = []  # handled by our middleware
    logging.getLogger("uvicorn.error").handlers = []

    # Re-propagate uvicorn logs to root
    # (Implementation detail: Uvicorn log config is often handled at run-time,
    # ensuring we capture it here or allow uvicorn to handle its own valid json is a choice.
    # We will stick to configuring the root logger.)

    return structlog.get_logger()


logger = structlog.get_logger()