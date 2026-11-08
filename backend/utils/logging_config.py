"""Logging setup."""
from __future__ import annotations

import logging

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Attach a single console handler to the root logger (idempotent)."""
    root = logging.getLogger()
    if not any(getattr(h, "_asm_handler", False) for h in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        handler._asm_handler = True  # marker to avoid duplicate handlers
        root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
