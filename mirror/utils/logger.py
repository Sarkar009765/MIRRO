import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "database"
LOG_DIR.mkdir(exist_ok=True)

_loggers = {}


def get_logger(name, level=logging.INFO):
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    fh = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}.log", maxBytes=5_242_880, backupCount=3
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    _loggers[name] = logger
    return logger


class ActivityLogger:
    def __init__(self, db):
        self.db = db

    def log(self, module, action, status="info", detail=None, duration_ms=None):
        self.db.execute(
            """INSERT INTO activity_logs (module, action, status, detail, duration_ms)
               VALUES (?, ?, ?, ?, ?)""",
            (module, action, status, detail, duration_ms)
        )

    def log_api(self, provider, endpoint, tokens_used=0, latency_ms=0, status="success"):
        self.db.execute(
            """INSERT INTO api_usage (provider, endpoint, tokens_used, latency_ms, status)
               VALUES (?, ?, ?, ?, ?)""",
            (provider, endpoint, tokens_used, latency_ms, status)
        )

    def log_error(self, module, error_type, error_message, traceback=None, recovered=False):
        self.db.execute(
            """INSERT INTO errors (module, error_type, error_message, traceback, recovered)
               VALUES (?, ?, ?, ?, ?)""",
            (module, error_type, error_message, traceback, recovered)
        )
