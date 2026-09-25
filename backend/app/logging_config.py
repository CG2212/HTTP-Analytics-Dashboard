import logging
import sys
from app.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT

def setup_logging():
    """Initializes global logging handlers for console and file output."""
    formatter = logging.Formatter(LOG_FORMAT)
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Clear existing handlers to prevent duplicate entries
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 1. Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. File Handler (app.log)
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Reduce noisy third-party logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def get_logger(module_name: str) -> logging.Logger:
    """Utility function to create named loggers in individual files."""
    return logging.getLogger(module_name)