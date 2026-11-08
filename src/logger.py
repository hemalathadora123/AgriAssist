"""
logger.py

Centralized logging utility for AgriAssist.

Every module imports this logger instead of using print().
"""

import logging
from pathlib import Path

from config import LOG_DIR

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "agriassist.log"


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger