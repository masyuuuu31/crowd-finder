import logging
import os
from colorlog import ColoredFormatter

def setup_logger(name: str, level=logging.DEBUG, log_file: str=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = ColoredFormatter(
        fmt="%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    )
    
    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File Handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)
        
    return logger
