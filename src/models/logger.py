import logging
import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class Logger:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str = 'salary_analysis', 
                 log_level: str = 'INFO',
                 log_dir: Optional[str] = None,
                 console_output: bool = True,
                 file_output: bool = True):
        if Logger._initialized:
            return
        
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.handlers = []
        
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if console_output:
            self._add_console_handler()
        
        if file_output:
            self._add_file_handler(log_dir)
        
        Logger._initialized = True

    def _add_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'{self.name}_{datetime.now().strftime("%Y%m%d")}.log'
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str):
        self.logger.critical(message)

    def set_level(self, level: str):
        self.logger.setLevel(getattr(logging, level.upper()))

    @classmethod
    def get_logger(cls, name: str = 'salary_analysis') -> 'Logger':
        if cls._instance is None:
            return cls(name)
        return cls._instance

    @classmethod
    def get_instance(cls, name: str = 'salary_analysis') -> 'Logger':
        """获取Logger实例（别名方法，与其他模型保持一致）"""
        if cls._instance is None:
            return cls(name)
        return cls._instance


def get_logger(name: str = 'salary_analysis') -> Logger:
    return Logger.get_logger(name)
