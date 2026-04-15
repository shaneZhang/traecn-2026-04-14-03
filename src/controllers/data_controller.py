from typing import Optional, Callable, Dict, Any, List
import pandas as pd

from ..services.data_service import DataService
from ..services.processing_service import ProcessingService
from ..models.data_manager import DataManager, DataChangeType
from ..models.logger import Logger
from ..utils.exceptions import SalaryAnalysisError


class DataController:
    """数据控制器，处理数据相关的用户操作"""
    
    def __init__(self, data_service: Optional[DataService] = None,
                 processing_service: Optional[ProcessingService] = None,
                 data_manager: Optional[DataManager] = None):
        self.data_service = data_service or DataService()
        self.processing_service = processing_service or ProcessingService()
        self.data_manager = data_manager or DataManager.get_instance()
        self.logger = Logger.get_instance()
        
        self._error_handlers: List[Callable[[str], None]] = []
        self._success_handlers: List[Callable[[str], None]] = []
    
    def add_error_handler(self, handler: Callable[[str], None]):
        """添加错误处理器"""
        self._error_handlers.append(handler)
    
    def add_success_handler(self, handler: Callable[[str], None]):
        """添加成功处理器"""
        self._success_handlers.append(handler)
    
    def _notify_error(self, message: str):
        """通知错误"""
        self.logger.error(message)
        for handler in self._error_handlers:
            handler(message)
    
    def _notify_success(self, message: str):
        """通知成功"""
        self.logger.info(message)
        for handler in self._success_handlers:
            handler(message)
    
    def load_file(self, file_path: Optional[str] = None) -> bool:
        """加载文件"""
        try:
            if file_path is None:
                return False
            
            data = self.data_service.load_excel(file_path)
            self.data_manager.load_data(data, source=file_path)
            
            self._notify_success(f"成功加载数据，共 {len(data)} 条记录")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"加载文件时发生未知错误: {str(e)}")
            return False
    
    def load_folder(self, folder_path: Optional[str] = None) -> bool:
        """加载文件夹"""
        try:
            if folder_path is None:
                return False
            
            data = self.data_service.load_folder(folder_path)
            self.data_manager.load_data(data, source=folder_path)
            
            self._notify_success(f"成功加载文件夹数据，共 {len(data)} 条记录")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"加载文件夹时发生未知错误: {str(e)}")
            return False
    
    def export_data(self, output_path: str, format: str = 'excel') -> bool:
        """导出数据"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可导出的数据")
                return False
            
            self.data_service.export_data(data, output_path, format)
            self._notify_success(f"数据已导出到: {output_path}")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"导出数据时发生未知错误: {str(e)}")
            return False
    
    def clean_duplicates(self) -> bool:
        """清洗重复数据"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可清洗的数据")
                return False
            
            cleaned_data, removed_count = self.processing_service.remove_duplicates(data)
            self.data_manager.update_data(cleaned_data, DataChangeType.CLEANED,
                                        {'removed_duplicates': removed_count})
            
            self._notify_success(f"删除了 {removed_count} 条重复记录")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"清洗重复数据时发生未知错误: {str(e)}")
            return False
    
    def clean_missing_values(self, strategy: str = 'drop') -> bool:
        """清洗缺失值"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可清洗的数据")
                return False
            
            cleaned_data, result_info = self.processing_service.handle_missing_values(data, strategy)
            self.data_manager.update_data(cleaned_data, DataChangeType.CLEANED,
                                        {'missing_value_strategy': strategy, 'affected_columns': result_info})
            
            if strategy == 'drop':
                removed_count = len(data) - len(cleaned_data)
                self._notify_success(f"删除了 {removed_count} 条含缺失值记录")
            else:
                self._notify_success(f"已用{strategy}策略填充缺失值")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"清洗缺失值时发生未知错误: {str(e)}")
            return False
    
    def remove_outliers(self, column: str, method: str = 'iqr', threshold: float = 1.5) -> bool:
        """移除异常值"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可处理的数据")
                return False
            
            cleaned_data, removed_count = self.processing_service.remove_outliers(data, column, method, threshold)
            self.data_manager.update_data(cleaned_data, DataChangeType.CLEANED,
                                        {'removed_outliers': removed_count, 'column': column})
            
            self._notify_success(f"移除了 {removed_count} 条异常值记录")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"移除异常值时发生未知错误: {str(e)}")
            return False
    
    def create_age_group(self) -> bool:
        """创建年龄分组"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可处理的数据")
                return False
            
            grouped_data = self.processing_service.create_age_group(data)
            self.data_manager.update_data(grouped_data, DataChangeType.GROUPED,
                                        {'group_type': 'age'})
            
            self._notify_success("已创建年龄分组字段: age_group")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建年龄分组时发生未知错误: {str(e)}")
            return False
    
    def create_salary_group(self, salary_column: str = 'pre_tax_salary') -> bool:
        """创建薪资分组"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可处理的数据")
                return False
            
            grouped_data = self.processing_service.create_salary_group(data, salary_column)
            self.data_manager.update_data(grouped_data, DataChangeType.GROUPED,
                                        {'group_type': 'salary'})
            
            self._notify_success("已创建薪资分组字段: salary_group")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建薪资分组时发生未知错误: {str(e)}")
            return False
    
    def create_experience_group(self) -> bool:
        """创建工作年限分组"""
        try:
            data = self.data_manager.get_data()
            if data is None:
                self._notify_error("没有可处理的数据")
                return False
            
            grouped_data = self.processing_service.create_work_experience_group(data)
            self.data_manager.update_data(grouped_data, DataChangeType.GROUPED,
                                        {'group_type': 'experience'})
            
            self._notify_success("已创建工作年限分组字段: experience_group")
            return True
        except SalaryAnalysisError as e:
            self._notify_error(str(e))
            return False
        except Exception as e:
            self._notify_error(f"创建工作年限分组时发生未知错误: {str(e)}")
            return False
    
    def reset_data(self) -> bool:
        """重置数据"""
        try:
            self.data_manager.reset_data()
            self._notify_success("数据已重置")
            return True
        except Exception as e:
            self._notify_error(f"重置数据时发生错误: {str(e)}")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要"""
        return self.data_manager.get_data_summary()
    
    def get_column_info(self) -> Dict[str, Dict[str, Any]]:
        """获取列信息"""
        return self.data_manager.get_column_info()
    
    def has_data(self) -> bool:
        """检查是否有数据"""
        return self.data_manager.has_data()
    
    def subscribe_to_data_changes(self, callback: Callable):
        """订阅数据变更"""
        return self.data_manager.subscribe(callback)
