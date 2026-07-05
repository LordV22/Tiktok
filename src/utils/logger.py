import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "videobot",
    level: str = "INFO",
    log_dir: Optional[Path] = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"bot_{datetime.now():%Y%m%d}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger


class SecurityFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.sensitive = ["token", "key", "secret", "password", "api_key"]

    def filter(self, record):
        msg = record.getMessage().lower()
        for word in self.sensitive:
            if word in msg:
                record.msg = "[BLOQUEADO - dados sensíveis]"
                record.args = ()
        return True
