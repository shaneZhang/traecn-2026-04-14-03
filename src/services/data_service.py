from typing import Optional, List, Dict, Tuple
import pandas as pd
import os

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from .data_loader_service import DataLoader, DataLoadError, DataValidationError


class DataService:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('DataService')
        self.loader = DataLoader(self.config)
    
    def load_file(self, file_path: str) -> Tuple[bool, str]:
        try:
            data = self.loader.load_excel(file_path)
            self.data_manager.set_data(data, is_original=True, message=f"从文件加载: {file_path}")
            self.logger.info(f"成功加载文件: {file_path}, 共 {len(data)} 条记录")
            return True, f"数据加载成功！共 {len(data)} 条记录"
        except DataLoadError as e:
            self.logger.error(f"加载文件失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.exception(f"加载文件时发生未知错误: {str(e)}")
            return False, f"加载失败: {str(e)}"
    
    def load_folder(self, folder_path: str) -> Tuple[bool, str]:
        try:
            data = self.loader.load_folder(folder_path)
            self.data_manager.set_data(data, is_original=True, message=f"从文件夹加载: {folder_path}")
            self.logger.info(f"成功加载文件夹: {folder_path}, 共 {len(data)} 条记录")
            return True, f"数据加载成功！共 {len(data)} 条记录"
        except DataLoadError as e:
            self.logger.error(f"加载文件夹失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.exception(f"加载文件夹时发生未知错误: {str(e)}")
            return False, f"加载失败: {str(e)}"
    
    def export_data(self, output_path: str, format: str = 'excel') -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可导出的数据"
        
        try:
            self.loader.export_data(data, output_path, format)
            self.logger.info(f"数据已导出到: {output_path}")
            return True, f"数据已导出到: {output_path}"
        except (DataLoadError, DataValidationError) as e:
            self.logger.error(f"导出数据失败: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.exception(f"导出数据时发生未知错误: {str(e)}")
            return False, f"导出失败: {str(e)}"
    
    def get_data_info(self) -> Dict:
        return self.data_manager.get_data_info()
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        data = self.data_manager.get_data()
        if data is None:
            return False, ["没有加载数据"]
        
        self.loader.data = data
        return self.loader.validate_data()
    
    def get_preview(self, n: int = 10) -> Optional[pd.DataFrame]:
        data = self.data_manager.get_data()
        if data is None:
            return None
        return data.head(n)
