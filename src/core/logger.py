"""Structured logging configuration."""
import structlog
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from .config import settings


def setup_logging() -> structlog.BoundLogger:
    """Configure structured logging."""
    
    # Ensure logs directory exists
    Path(settings.logs_dir).mkdir(exist_ok=True)
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger("twitter_bot")


def log_step(step: str, **kwargs: Any) -> Dict[str, Any]:
    """Create a log context for a processing step."""
    return {"step": step, **kwargs}


# Global logger instance
logger = setup_logging()