import logging
import os
from colorlog import ColoredFormatter
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

def _create_file_handler(log_file: str) -> TimedRotatingFileHandler:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=False
    )
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)
    file_handler.setFormatter(file_formatter)
    return file_handler

def attach_uvicorn_loggers(log_file: str):
    file_handler = _create_file_handler(log_file)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.addHandler(file_handler)

def setup_logger(name: str, level=logging.DEBUG, log_file: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger  # ハンドラがすでに設定済みなら再設定しない

    # カラーフォーマッタ（コンソール用）
    formatter = ColoredFormatter(
        fmt="%(log_color)s" + LOG_FORMAT,
        datefmt=LOG_DATEFMT,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    # コンソール出力
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # ファイル出力（オプション）
    if log_file:
        file_handler = _create_file_handler(log_file)
        logger.addHandler(file_handler)

    return logger
