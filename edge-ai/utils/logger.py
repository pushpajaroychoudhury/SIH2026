"""
Shared logger for all edge-ai modules.
Writes to console + a rotating file so field devices keep a local audit trail
even when offline.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, log_dir: str = "logs/", level: str = "INFO") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        # already configured (avoid duplicate handlers on re-import)
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"), maxBytes=5_000_000, backupCount=5
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
