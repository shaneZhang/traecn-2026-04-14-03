from typing import Optional, Callable, Dict, Any
import pandas as pd

from ..models.data_manager import DataManager
from ..models.config_manager import ConfigManager
from ..models.logger import get_logger
from ..services.analysis_service import AnalysisService, DataAnalysisError


class AnalysisController:
    def __init__(self, data_manager: DataManager, config: Optional[ConfigManager] = None):
        self.data_manager = data_manager
        self.config = config or ConfigManager()
        self.logger = get_logger('AnalysisController')
        self.analysis_service = AnalysisService(data_manager, self.config)
    
    def get_descriptive_stats(self, column: str) -> Dict[str, Any]:
        try:
            return self.analysis_service.get_descriptive_stats(column)
        except DataAnalysisError as e:
            self.logger.error(f"获取描述性统计失败: {str(e)}")
            return {}
    
    def get_frequency_analysis(self, column: str) -> pd.DataFrame:
        try:
            return self.analysis_service.get_frequency_analysis(column)
        except DataAnalysisError as e:
            self.logger.error(f"频率分析失败: {str(e)}")
            return pd.DataFrame()
    
    def get_crosstab(self, row_col: str, col_col: str) -> pd.DataFrame:
        try:
            return self.analysis_service.get_crosstab(row_col, col_col)
        except DataAnalysisError as e:
            self.logger.error(f"交叉分析失败: {str(e)}")
            return pd.DataFrame()
    
    def compare_by_dimension(self, dimension: str, value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        try:
            return self.analysis_service.compare_by_dimension(dimension, value_col)
        except DataAnalysisError as e:
            self.logger.error(f"维度对比分析失败: {str(e)}")
            return pd.DataFrame()
    
    def get_correlation_matrix(self, columns: list = None) -> pd.DataFrame:
        try:
            return self.analysis_service.get_correlation_matrix(columns)
        except DataAnalysisError as e:
            self.logger.error(f"相关性分析失败: {str(e)}")
            return pd.DataFrame()
    
    def get_correlation(self, col1: str, col2: str) -> Dict[str, float]:
        try:
            return self.analysis_service.get_correlation(col1, col2)
        except DataAnalysisError as e:
            self.logger.error(f"相关性计算失败: {str(e)}")
            return {}
    
    def get_trend_analysis(self, time_col: str, value_col: str = 'pre_tax_salary') -> pd.DataFrame:
        try:
            return self.analysis_service.get_trend_analysis(time_col, value_col)
        except DataAnalysisError as e:
            self.logger.error(f"趋势分析失败: {str(e)}")
            return pd.DataFrame()
    
    def get_summary_report(self, salary_col: str = 'pre_tax_salary') -> Dict[str, Any]:
        try:
            return self.analysis_service.get_summary_report(salary_col)
        except DataAnalysisError as e:
            self.logger.error(f"获取摘要报告失败: {str(e)}")
            return {}
    
    def get_boxplot_data(self, group_by: str, value_col: str) -> Dict[str, Dict]:
        try:
            return self.analysis_service.get_boxplot_data(group_by, value_col)
        except DataAnalysisError as e:
            self.logger.error(f"获取箱线图数据失败: {str(e)}")
            return {}
    
    def get_salary_distribution(self, salary_col: str = 'pre_tax_salary') -> pd.DataFrame:
        try:
            return self.analysis_service.get_salary_distribution(salary_col)
        except DataAnalysisError as e:
            self.logger.error(f"获取薪资分布失败: {str(e)}")
            return pd.DataFrame()
    
    def has_data(self) -> bool:
        return self.data_manager.has_data()
    
    def format_stats_result(self, stats: Dict[str, Any], column: str) -> str:
        if not stats:
            return f"无法获取 '{column}' 的统计数据"
        
        result = f"薪资字段: {column}\n{'='*40}\n\n"
        for key, value in stats.items():
            if value is not None:
                if isinstance(value, float):
                    result += f"{key}: {value:,.2f}\n"
                else:
                    result += f"{key}: {value}\n"
        
        return result
    
    def format_frequency_result(self, freq: pd.DataFrame, column: str) -> str:
        if freq.empty:
            return f"无法获取 '{column}' 的频率分析"
        
        result = f"频率分析: {column}\n{'='*40}\n\n"
        result += freq.to_string(index=False)
        return result
    
    def format_crosstab_result(self, crosstab: pd.DataFrame, row_col: str) -> str:
        if crosstab.empty:
            return "无法生成交叉分析"
        
        result = f"交叉分析: {row_col}\n{'='*40}\n\n"
        result += crosstab.to_string()
        return result
