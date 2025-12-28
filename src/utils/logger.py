"""Logging utilities and configuration."""

import logging
import sys
from typing import Optional

from src.core.constants import WorkerConfig


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name: Logger name
        level: Logging level
        log_format: Custom log format
        date_format: Custom date format
        
    Returns:
        Configured logger instance
    """
    log_format = log_format or WorkerConfig.LOG_FORMAT
    date_format = date_format or WorkerConfig.LOG_DATE_FORMAT
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name."""
    return logging.getLogger(name)
