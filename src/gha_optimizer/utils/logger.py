"""Logging utilities for GHA-Optimizer."""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "gha-optimizer", verbose: bool = False) -> logging.Logger:
    """
    Set up logger with appropriate configuration.

    Args:
        name: Logger name
        verbose: Enable verbose (DEBUG) logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Don't add handlers if already configured
    if logger.handlers:
        return logger

    # Set log level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Create formatter
    if verbose:
        # Detailed format for verbose mode
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Simple format for normal mode
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to avoid duplicate messages
    logger.propagate = False

    # Configure the gha_optimizer package logger to use the same handler
    package_logger = logging.getLogger("gha_optimizer")
    if not package_logger.handlers:
        package_logger.setLevel(level)
        package_logger.addHandler(handler)
        package_logger.propagate = False

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get existing logger instance.

    Args:
        name: Logger name (defaults to "gha-optimizer")

    Returns:
        Logger instance
    """
    return logging.getLogger(name or "gha-optimizer")
