import logging
import os
from datetime import datetime
from typing import Optional, Dict


_loggers: Dict[str, 'LoggerInstance'] = {}


class LoggerInstance:
    def __init__(self, name: str = 'SalaryAnalysis'):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()
        
        self._log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self._log_dir, exist_ok=True)
        
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        log_file = os.path.join(self._log_dir, f'salary_analysis_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
    
    def set_level(self, level: str) -> None:
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self._logger.setLevel(level_map.get(level.upper(), logging.INFO))
    
    def debug(self, message: str) -> None:
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str) -> None:
        self._logger.critical(message)
    
    def exception(self, message: str) -> None:
        self._logger.exception(message)


class Logger:
    def __new__(cls, name: str = 'SalaryAnalysis') -> LoggerInstance:
        if name not in _loggers:
            _loggers[name] = LoggerInstance(name)
        return _loggers[name]


def get_logger(name: str = 'SalaryAnalysis') -> LoggerInstance:
    return Logger(name)
