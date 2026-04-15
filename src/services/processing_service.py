from typing import Optional, List, Dict, Any, Tuple
import pandas as pd

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from .data_processor_service import DataProcessor, DataProcessingError


class ProcessingService:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('ProcessingService')
        self.processor = DataProcessor(self.config)
    
    def remove_duplicates(self) -> Tuple[bool, str, int]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据", 0
        
        try:
            result, count = self.processor.remove_duplicates(data)
            self.data_manager.update_data(result, f"删除了 {count} 条重复记录")
            self.logger.info(f"删除了 {count} 条重复记录")
            return True, f"删除了 {count} 条重复记录", count
        except DataProcessingError as e:
            self.logger.error(f"删除重复数据失败: {str(e)}")
            return False, str(e), 0
    
    def handle_missing_values(self, strategy: str = 'drop',
                             columns: Optional[List[str]] = None) -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据"
        
        try:
            result, processed = self.processor.handle_missing_values(data, strategy, columns)
            
            if strategy == 'drop':
                count = len(data) - len(result)
                msg = f"删除了 {count} 条含缺失值记录"
            else:
                count = sum(processed.values())
                msg = f"处理了 {count} 个缺失值"
            
            self.data_manager.update_data(result, msg)
            self.logger.info(msg)
            return True, msg
        except DataProcessingError as e:
            self.logger.error(f"处理缺失值失败: {str(e)}")
            return False, str(e)
    
    def remove_outliers(self, column: str, method: str = 'iqr',
                       threshold: float = None) -> Tuple[bool, str, int]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据", 0
        
        try:
            result, count = self.processor.remove_outliers(data, column, method, threshold)
            self.data_manager.update_data(result, f"移除了 {count} 条异常值记录")
            self.logger.info(f"从列 '{column}' 移除了 {count} 条异常值记录")
            return True, f"移除了 {count} 条异常值记录", count
        except DataProcessingError as e:
            self.logger.error(f"移除异常值失败: {str(e)}")
            return False, str(e), 0
    
    def create_age_group(self, age_column: str = 'age') -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据"
        
        try:
            result = self.processor.create_age_group(data, age_column)
            self.data_manager.update_data(result, "创建了年龄分组字段: age_group")
            self.logger.info(f"创建了年龄分组字段: age_group")
            return True, "已创建年龄分组字段: age_group"
        except DataProcessingError as e:
            self.logger.error(f"创建年龄分组失败: {str(e)}")
            return False, str(e)
    
    def create_salary_group(self, salary_column: str = 'pre_tax_salary') -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据"
        
        try:
            result = self.processor.create_salary_group(data, salary_column)
            self.data_manager.update_data(result, "创建了薪资分组字段: salary_group")
            self.logger.info(f"创建了薪资分组字段: salary_group")
            return True, "已创建薪资分组字段: salary_group"
        except DataProcessingError as e:
            self.logger.error(f"创建薪资分组失败: {str(e)}")
            return False, str(e)
    
    def create_experience_group(self, years_column: str = 'work_years') -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据"
        
        try:
            result = self.processor.create_work_experience_group(data, years_column)
            self.data_manager.update_data(result, "创建了工作年限分组字段: experience_group")
            self.logger.info(f"创建了工作年限分组字段: experience_group")
            return True, "已创建工作年限分组字段: experience_group"
        except DataProcessingError as e:
            self.logger.error(f"创建工作年限分组失败: {str(e)}")
            return False, str(e)
    
    def filter_data(self, conditions: Dict[str, Any]) -> Tuple[bool, str]:
        data = self.data_manager.get_data()
        if data is None:
            return False, "没有可处理的数据"
        
        try:
            result = self.processor.filter_data(data, conditions)
            count = len(data) - len(result)
            self.data_manager.update_data(result, f"筛选数据，移除了 {count} 条记录")
            self.logger.info(f"筛选数据，移除了 {count} 条记录")
            return True, f"筛选完成，保留了 {len(result)} 条记录"
        except DataProcessingError as e:
            self.logger.error(f"筛选数据失败: {str(e)}")
            return False, str(e)
    
    def reset_data(self) -> Tuple[bool, str]:
        success = self.data_manager.reset_data()
        if success:
            self.logger.info("数据已重置为原始状态")
            return True, "数据已重置"
        return False, "没有原始数据可重置"
    
    def get_data_summary(self) -> Dict[str, Any]:
        data = self.data_manager.get_data()
        if data is None:
            return {}
        return self.processor.get_data_summary(data)
