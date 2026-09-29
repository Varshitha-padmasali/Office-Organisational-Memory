"""
Centralized logging configuration.

Day 1 goal: consistent, readable logs across the app (no scattered
print() statements). This is intentionally simple — structured JSON
logging can be added later (Day 5+) if we ship to a real environment
with a log aggregator.
"""

import logging
import sys

from app.core.config import get_settings

settings = get_settings()

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """Configure the root logger once, at application startup."""
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Quiet down noisy third-party loggers unless we're actively debugging.
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(
            logging.DEBUG if settings.DEBUG else logging.WARNING
        )


def get_logger(name: str) -> logging.Logger:
    """Convenience helper so modules can do `logger = get_logger(__name__)`."""
    return logging.getLogger(name)
